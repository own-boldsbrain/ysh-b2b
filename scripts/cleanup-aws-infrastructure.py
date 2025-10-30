#!/usr/bin/env python3
"""
Script para limpar completamente a infraestrutura AWS YSH B2B
Prepara o ambiente para a nova arquitetura focada em Facebook Commerce
"""
import boto3
import json
import time
from datetime import datetime


class AWSCleaner:
    def __init__(self, profile_name="ysh-production", dry_run=True):
        self.session = boto3.Session(profile_name=profile_name)
        self.dry_run = dry_run
        self.region = self.session.region_name or "us-east-1"

        # Clients
        self.ecs = self.session.client("ecs")
        self.ec2 = self.session.client("ec2")
        self.elbv2 = self.session.client("elbv2")
        self.rds = self.session.client("rds")
        self.elasticache = self.session.client("elasticache")
        self.s3 = self.session.client("s3")
        self.cloudformation = self.session.client("cloudformation")
        self.logs = self.session.client("logs")

        self.resources_to_delete = []

    def log(self, message, level="INFO"):
        """Log com timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        prefix = "🔍 [DRY-RUN]" if self.dry_run else "🗑️  [DELETE]"
        print(f"{prefix} [{level}] {timestamp} - {message}")

    def confirm_action(self, message):
        """Solicita confirmação do usuário"""
        if self.dry_run:
            return True

        response = input(f"\n⚠️  {message}\nDigite 'CONFIRMAR' para continuar: ")
        return response == "CONFIRMAR"

    # ==========================================
    # 1. ECS SERVICES & TASKS
    # ==========================================

    def cleanup_ecs_services(self):
        """Remove services e tasks do ECS"""
        self.log("=" * 80)
        self.log("LIMPANDO ECS SERVICES & TASKS")
        self.log("=" * 80)

        try:
            # Listar clusters
            clusters = self.ecs.list_clusters()
            cluster_arns = clusters.get("clusterArns", [])

            if not cluster_arns:
                self.log("Nenhum cluster ECS encontrado", "INFO")
                return

            for cluster_arn in cluster_arns:
                cluster_name = cluster_arn.split("/")[-1]
                self.log(f"\n📦 Processando cluster: {cluster_name}")

                # Listar services
                services = self.ecs.list_services(cluster=cluster_arn)
                service_arns = services.get("serviceArns", [])

                for service_arn in service_arns:
                    service_name = service_arn.split("/")[-1]
                    self.log(f"   Service: {service_name}")
                    self.resources_to_delete.append(
                        {
                            "type": "ECS_SERVICE",
                            "name": service_name,
                            "cluster": cluster_name,
                            "arn": service_arn,
                        }
                    )

                    if not self.dry_run:
                        # Escalar para 0
                        self.log(f"      Escalando para 0 tasks...")
                        self.ecs.update_service(
                            cluster=cluster_arn, service=service_arn, desiredCount=0
                        )
                        time.sleep(5)

                        # Deletar service
                        self.log(f"      Deletando service...")
                        self.ecs.delete_service(
                            cluster=cluster_arn, service=service_arn, force=True
                        )

                # Listar tasks em execução
                tasks = self.ecs.list_tasks(cluster=cluster_arn)
                task_arns = tasks.get("taskArns", [])

                for task_arn in task_arns:
                    task_id = task_arn.split("/")[-1]
                    self.log(f"   Task: {task_id}")
                    self.resources_to_delete.append(
                        {"type": "ECS_TASK", "id": task_id, "arn": task_arn}
                    )

                    if not self.dry_run:
                        self.log(f"      Parando task...")
                        self.ecs.stop_task(cluster=cluster_arn, task=task_arn)

                # Aguardar services serem deletados
                if not self.dry_run and service_arns:
                    self.log(f"   Aguardando services serem deletados...")
                    time.sleep(30)

                # Deletar cluster
                self.resources_to_delete.append(
                    {"type": "ECS_CLUSTER", "name": cluster_name, "arn": cluster_arn}
                )

                if not self.dry_run:
                    self.log(f"   Deletando cluster...")
                    self.ecs.delete_cluster(cluster=cluster_arn)

        except Exception as e:
            self.log(f"Erro ao limpar ECS: {str(e)}", "ERROR")

    # ==========================================
    # 2. LOAD BALANCERS & TARGET GROUPS
    # ==========================================

    def cleanup_load_balancers(self):
        """Remove Load Balancers e Target Groups"""
        self.log("\n" + "=" * 80)
        self.log("LIMPANDO LOAD BALANCERS")
        self.log("=" * 80)

        try:
            # Listar ALBs
            lbs = self.elbv2.describe_load_balancers()

            for lb in lbs["LoadBalancers"]:
                lb_name = lb["LoadBalancerName"]
                lb_arn = lb["LoadBalancerArn"]

                if "ysh" in lb_name.lower():
                    self.log(f"\n⚖️  Load Balancer: {lb_name}")
                    self.resources_to_delete.append(
                        {"type": "LOAD_BALANCER", "name": lb_name, "arn": lb_arn}
                    )

                    if not self.dry_run:
                        self.log(f"   Deletando ALB...")
                        self.elbv2.delete_load_balancer(LoadBalancerArn=lb_arn)

            # Aguardar ALBs serem deletados
            if not self.dry_run:
                self.log("Aguardando ALBs serem deletados (30s)...")
                time.sleep(30)

            # Listar Target Groups
            tgs = self.elbv2.describe_target_groups()

            for tg in tgs["TargetGroups"]:
                tg_name = tg["TargetGroupName"]
                tg_arn = tg["TargetGroupArn"]

                if "ysh" in tg_name.lower():
                    self.log(f"\n🎯 Target Group: {tg_name}")
                    self.resources_to_delete.append(
                        {"type": "TARGET_GROUP", "name": tg_name, "arn": tg_arn}
                    )

                    if not self.dry_run:
                        self.log(f"   Deletando Target Group...")
                        self.elbv2.delete_target_group(TargetGroupArn=tg_arn)

        except Exception as e:
            self.log(f"Erro ao limpar Load Balancers: {str(e)}", "ERROR")

    # ==========================================
    # 3. RDS DATABASES
    # ==========================================

    def cleanup_rds(self):
        """Remove instâncias RDS"""
        self.log("\n" + "=" * 80)
        self.log("LIMPANDO RDS DATABASES")
        self.log("=" * 80)

        try:
            instances = self.rds.describe_db_instances()

            for instance in instances["DBInstances"]:
                db_id = instance["DBInstanceIdentifier"]

                if "ysh" in db_id.lower():
                    self.log(f"\n🗄️  RDS Instance: {db_id}")
                    self.resources_to_delete.append(
                        {
                            "type": "RDS_INSTANCE",
                            "id": db_id,
                            "engine": instance["Engine"],
                        }
                    )

                    if not self.dry_run:
                        self.log(f"   Deletando (sem snapshot final)...")
                        self.rds.delete_db_instance(
                            DBInstanceIdentifier=db_id,
                            SkipFinalSnapshot=True,
                            DeleteAutomatedBackups=True,
                        )

        except Exception as e:
            self.log(f"Erro ao limpar RDS: {str(e)}", "ERROR")

    # ==========================================
    # 4. ELASTICACHE (REDIS)
    # ==========================================

    def cleanup_elasticache(self):
        """Remove clusters Redis"""
        self.log("\n" + "=" * 80)
        self.log("LIMPANDO ELASTICACHE (REDIS)")
        self.log("=" * 80)

        try:
            clusters = self.elasticache.describe_cache_clusters()

            for cluster in clusters["CacheClusters"]:
                cluster_id = cluster["CacheClusterId"]

                if "ysh" in cluster_id.lower():
                    self.log(f"\n🔴 Redis Cluster: {cluster_id}")
                    self.resources_to_delete.append(
                        {"type": "ELASTICACHE_CLUSTER", "id": cluster_id}
                    )

                    if not self.dry_run:
                        self.log(f"   Deletando...")
                        self.elasticache.delete_cache_cluster(CacheClusterId=cluster_id)

        except Exception as e:
            self.log(f"Erro ao limpar ElastiCache: {str(e)}", "ERROR")

    # ==========================================
    # 5. S3 BUCKETS
    # ==========================================

    def cleanup_s3_buckets(self):
        """Remove buckets S3 e seus conteúdos"""
        self.log("\n" + "=" * 80)
        self.log("LIMPANDO S3 BUCKETS")
        self.log("=" * 80)

        try:
            buckets = self.s3.list_buckets()

            for bucket in buckets["Buckets"]:
                bucket_name = bucket["Name"]

                if "ysh" in bucket_name.lower() and "media" in bucket_name.lower():
                    self.log(f"\n📦 S3 Bucket: {bucket_name}")

                    # Contar objetos
                    s3_resource = self.session.resource("s3")
                    bucket_resource = s3_resource.Bucket(bucket_name)
                    object_count = sum(1 for _ in bucket_resource.objects.all())

                    self.log(f"   Objetos: {object_count}")
                    self.resources_to_delete.append(
                        {
                            "type": "S3_BUCKET",
                            "name": bucket_name,
                            "objects": object_count,
                        }
                    )

                    if not self.dry_run:
                        if object_count > 0:
                            self.log(f"   Deletando {object_count} objetos...")
                            bucket_resource.objects.all().delete()

                        self.log(f"   Deletando bucket...")
                        self.s3.delete_bucket(Bucket=bucket_name)

        except Exception as e:
            self.log(f"Erro ao limpar S3: {str(e)}", "ERROR")

    # ==========================================
    # 6. CLOUDWATCH LOGS
    # ==========================================

    def cleanup_cloudwatch_logs(self):
        """Remove log groups do CloudWatch"""
        self.log("\n" + "=" * 80)
        self.log("LIMPANDO CLOUDWATCH LOGS")
        self.log("=" * 80)

        try:
            log_groups = self.logs.describe_log_groups()

            for group in log_groups["logGroups"]:
                group_name = group["logGroupName"]

                if "ysh" in group_name.lower() or "ecs" in group_name.lower():
                    self.log(f"\n📊 Log Group: {group_name}")
                    self.resources_to_delete.append(
                        {"type": "LOG_GROUP", "name": group_name}
                    )

                    if not self.dry_run:
                        self.log(f"   Deletando...")
                        self.logs.delete_log_group(logGroupName=group_name)

        except Exception as e:
            self.log(f"Erro ao limpar CloudWatch Logs: {str(e)}", "ERROR")

    # ==========================================
    # 7. SECURITY GROUPS & VPC
    # ==========================================

    def cleanup_networking(self):
        """Remove Security Groups e VPC"""
        self.log("\n" + "=" * 80)
        self.log("LIMPANDO NETWORKING (VPC, SECURITY GROUPS)")
        self.log("=" * 80)

        try:
            # Listar VPCs
            vpcs = self.ec2.describe_vpcs()

            for vpc in vpcs["Vpcs"]:
                vpc_id = vpc["VpcId"]

                # Verificar tags
                tags = {tag["Key"]: tag["Value"] for tag in vpc.get("Tags", [])}
                vpc_name = tags.get("Name", "")

                if "ysh" in vpc_name.lower():
                    self.log(f"\n🌐 VPC: {vpc_name} ({vpc_id})")

                    # Listar Security Groups
                    sgs = self.ec2.describe_security_groups(
                        Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
                    )

                    for sg in sgs["SecurityGroups"]:
                        sg_id = sg["GroupId"]
                        sg_name = sg["GroupName"]

                        # Não deletar default SG
                        if sg_name != "default":
                            self.log(f"   Security Group: {sg_name} ({sg_id})")
                            self.resources_to_delete.append(
                                {"type": "SECURITY_GROUP", "id": sg_id, "name": sg_name}
                            )

                            if not self.dry_run:
                                try:
                                    self.log(f"      Deletando...")
                                    self.ec2.delete_security_group(GroupId=sg_id)
                                except Exception as e:
                                    self.log(f"      Erro: {str(e)}", "WARN")

                    # Listar Subnets
                    subnets = self.ec2.describe_subnets(
                        Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
                    )

                    for subnet in subnets["Subnets"]:
                        subnet_id = subnet["SubnetId"]
                        self.log(f"   Subnet: {subnet_id}")
                        self.resources_to_delete.append(
                            {"type": "SUBNET", "id": subnet_id}
                        )

                        if not self.dry_run:
                            self.log(f"      Deletando...")
                            self.ec2.delete_subnet(SubnetId=subnet_id)

                    # Listar Internet Gateways
                    igws = self.ec2.describe_internet_gateways(
                        Filters=[{"Name": "attachment.vpc-id", "Values": [vpc_id]}]
                    )

                    for igw in igws["InternetGateways"]:
                        igw_id = igw["InternetGatewayId"]
                        self.log(f"   Internet Gateway: {igw_id}")
                        self.resources_to_delete.append(
                            {"type": "INTERNET_GATEWAY", "id": igw_id}
                        )

                        if not self.dry_run:
                            self.log(f"      Desanexando...")
                            self.ec2.detach_internet_gateway(
                                InternetGatewayId=igw_id, VpcId=vpc_id
                            )
                            self.log(f"      Deletando...")
                            self.ec2.delete_internet_gateway(InternetGatewayId=igw_id)

                    # Deletar VPC
                    self.resources_to_delete.append(
                        {"type": "VPC", "id": vpc_id, "name": vpc_name}
                    )

                    if not self.dry_run:
                        self.log(f"   Deletando VPC...")
                        self.ec2.delete_vpc(VpcId=vpc_id)

        except Exception as e:
            self.log(f"Erro ao limpar Networking: {str(e)}", "ERROR")

    # ==========================================
    # 8. CLOUDFORMATION STACKS
    # ==========================================

    def cleanup_cloudformation(self):
        """Remove stacks do CloudFormation"""
        self.log("\n" + "=" * 80)
        self.log("LIMPANDO CLOUDFORMATION STACKS")
        self.log("=" * 80)

        try:
            stacks = self.cloudformation.list_stacks(
                StackStatusFilter=[
                    "CREATE_COMPLETE",
                    "UPDATE_COMPLETE",
                    "UPDATE_ROLLBACK_COMPLETE",
                ]
            )

            for stack in stacks["StackSummaries"]:
                stack_name = stack["StackName"]

                if "ysh" in stack_name.lower():
                    self.log(f"\n☁️  CloudFormation Stack: {stack_name}")
                    self.resources_to_delete.append(
                        {"type": "CLOUDFORMATION_STACK", "name": stack_name}
                    )

                    if not self.dry_run:
                        self.log(f"   Deletando stack...")
                        self.cloudformation.delete_stack(StackName=stack_name)

        except Exception as e:
            self.log(f"Erro ao limpar CloudFormation: {str(e)}", "ERROR")

    # ==========================================
    # ORQUESTRADOR PRINCIPAL
    # ==========================================

    def cleanup_all(self):
        """Executa limpeza completa na ordem correta"""
        self.log("\n" + "=" * 80)
        self.log("INICIANDO LIMPEZA COMPLETA DA INFRAESTRUTURA AWS YSH B2B")
        self.log("=" * 80)

        if self.dry_run:
            self.log("⚠️  MODO DRY-RUN ATIVADO - Nenhum recurso será deletado", "WARN")
        else:
            if not self.confirm_action(
                "ATENÇÃO: Esta ação irá DELETAR PERMANENTEMENTE todos os recursos AWS YSH B2B!\n"
                "Isso inclui: ECS, RDS, Redis, S3, Load Balancers, VPC, etc.\n"
                "Esta ação é IRREVERSÍVEL!"
            ):
                self.log("Operação cancelada pelo usuário", "INFO")
                return

        # Ordem de limpeza (do mais dependente ao menos dependente)
        self.cleanup_ecs_services()  # 1. ECS Services & Tasks
        self.cleanup_load_balancers()  # 2. Load Balancers & Target Groups
        self.cleanup_rds()  # 3. RDS Databases
        self.cleanup_elasticache()  # 4. ElastiCache Redis
        self.cleanup_cloudwatch_logs()  # 5. CloudWatch Logs
        self.cleanup_s3_buckets()  # 6. S3 Buckets
        self.cleanup_cloudformation()  # 7. CloudFormation Stacks
        time.sleep(10)  # Aguardar dependências
        self.cleanup_networking()  # 8. VPC, Subnets, Security Groups (por último)

        # Resumo
        self.print_summary()

    def print_summary(self):
        """Imprime resumo de recursos a serem deletados"""
        self.log("\n" + "=" * 80)
        self.log("RESUMO DE RECURSOS")
        self.log("=" * 80)

        # Agrupar por tipo
        by_type = {}
        for resource in self.resources_to_delete:
            res_type = resource["type"]
            by_type[res_type] = by_type.get(res_type, 0) + 1

        total = len(self.resources_to_delete)

        self.log(f"\n📊 Total de recursos: {total}\n")

        for res_type, count in sorted(by_type.items()):
            self.log(f"   {res_type}: {count}")

        if self.dry_run:
            self.log("\n✅ DRY-RUN COMPLETO - Nenhum recurso foi deletado", "INFO")
            self.log("\nPara executar a limpeza real, execute:", "INFO")
            self.log(
                "   python scripts/cleanup-aws-infrastructure.py --confirm", "INFO"
            )
        else:
            self.log("\n✅ LIMPEZA COMPLETA EXECUTADA", "SUCCESS")
            self.log(
                "\nAmbiente AWS limpo e pronto para nova arquitetura Facebook Commerce! 🚀",
                "SUCCESS",
            )


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Limpa infraestrutura AWS YSH B2B para preparar nova arquitetura"
    )
    parser.add_argument(
        "--profile",
        default="ysh-production",
        help="AWS profile name (default: ysh-production)",
    )
    parser.add_argument(
        "--confirm", action="store_true", help="Executar limpeza real (sem dry-run)"
    )
    parser.add_argument(
        "--region", default="us-east-1", help="AWS region (default: us-east-1)"
    )

    args = parser.parse_args()

    # Banner
    print("\n" + "=" * 80)
    print("AWS INFRASTRUCTURE CLEANUP - YSH B2B Platform")
    print("Preparação para Nova Arquitetura Facebook Commerce")
    print("=" * 80 + "\n")

    # Criar cleaner
    cleaner = AWSCleaner(profile_name=args.profile, dry_run=not args.confirm)

    # Executar limpeza
    cleaner.cleanup_all()


if __name__ == "__main__":
    main()
