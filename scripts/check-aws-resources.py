#!/usr/bin/env python3
"""
Script para verificar recursos AWS (S3 e EC2) no perfil ysh-production
"""
import boto3
import json
from datetime import datetime


def format_datetime(dt):
    """Formata datetime para string legível"""
    if isinstance(dt, datetime):
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return str(dt)


def check_s3_buckets(session):
    """Lista todos os buckets S3 e seus conteúdos"""
    s3 = session.client("s3")
    s3_resource = session.resource("s3")

    print("\n" + "=" * 80)
    print("BUCKETS S3")
    print("=" * 80)

    try:
        response = s3.list_buckets()
        buckets = response.get("Buckets", [])

        if not buckets:
            print("❌ Nenhum bucket S3 encontrado")
            return

        print(f"✅ Total de buckets: {len(buckets)}\n")

        for bucket in buckets:
            bucket_name = bucket["Name"]
            creation_date = format_datetime(bucket["CreationDate"])

            print(f"\n📦 Bucket: {bucket_name}")
            print(f"   Criado em: {creation_date}")

            # Verificar região
            try:
                location = s3.get_bucket_location(Bucket=bucket_name)
                region = location.get("LocationConstraint") or "us-east-1"
                print(f"   Região: {region}")
            except Exception as e:
                print(f"   Região: Erro ao obter ({str(e)})")

            # Verificar tamanho e quantidade de objetos
            try:
                bucket_resource = s3_resource.Bucket(bucket_name)
                total_size = 0
                object_count = 0

                for obj in bucket_resource.objects.all():
                    total_size += obj.size
                    object_count += 1

                size_mb = total_size / (1024 * 1024)
                size_gb = total_size / (1024 * 1024 * 1024)

                print(f"   Objetos: {object_count}")
                if size_gb >= 1:
                    print(f"   Tamanho total: {size_gb:.2f} GB")
                else:
                    print(f"   Tamanho total: {size_mb:.2f} MB")

                # Listar alguns objetos de exemplo
                if object_count > 0:
                    print(f"\n   📄 Primeiros 10 objetos:")
                    for i, obj in enumerate(list(bucket_resource.objects.all())[:10]):
                        obj_size_kb = obj.size / 1024
                        print(f"      {i+1}. {obj.key} ({obj_size_kb:.2f} KB)")

                    if object_count > 10:
                        print(f"      ... e mais {object_count - 10} objetos")

            except Exception as e:
                print(f"   ⚠️  Erro ao listar objetos: {str(e)}")

            # Verificar tags
            try:
                tags = s3.get_bucket_tagging(Bucket=bucket_name)
                if tags.get("TagSet"):
                    print(f"   Tags:")
                    for tag in tags["TagSet"]:
                        print(f"      - {tag['Key']}: {tag['Value']}")
            except:
                pass

    except Exception as e:
        print(f"❌ Erro ao listar buckets S3: {str(e)}")


def check_ec2_instances(session):
    """Lista todas as instâncias EC2"""
    ec2 = session.client("ec2")

    print("\n" + "=" * 80)
    print("INSTÂNCIAS EC2")
    print("=" * 80)

    try:
        response = ec2.describe_instances()

        instance_count = 0
        for reservation in response["Reservations"]:
            for instance in reservation["Instances"]:
                instance_count += 1
                instance_id = instance["InstanceId"]
                instance_type = instance["InstanceType"]
                state = instance["State"]["Name"]
                launch_time = format_datetime(instance.get("LaunchTime"))

                print(f"\n🖥️  Instância: {instance_id}")
                print(f"   Tipo: {instance_type}")
                print(f"   Estado: {state}")
                print(f"   Lançada em: {launch_time}")

                # IP público
                if instance.get("PublicIpAddress"):
                    print(f"   IP Público: {instance['PublicIpAddress']}")

                # IP privado
                if instance.get("PrivateIpAddress"):
                    print(f"   IP Privado: {instance['PrivateIpAddress']}")

                # VPC
                if instance.get("VpcId"):
                    print(f"   VPC: {instance['VpcId']}")

                # Tags
                if instance.get("Tags"):
                    print(f"   Tags:")
                    for tag in instance["Tags"]:
                        print(f"      - {tag['Key']}: {tag['Value']}")

        if instance_count == 0:
            print("❌ Nenhuma instância EC2 encontrada")
        else:
            print(f"\n✅ Total de instâncias: {instance_count}")

    except Exception as e:
        print(f"❌ Erro ao listar instâncias EC2: {str(e)}")


def check_ecs_clusters(session):
    """Lista clusters ECS e suas tasks"""
    ecs = session.client("ecs")

    print("\n" + "=" * 80)
    print("CLUSTERS ECS (Fargate)")
    print("=" * 80)

    try:
        clusters = ecs.list_clusters()
        cluster_arns = clusters.get("clusterArns", [])

        if not cluster_arns:
            print("❌ Nenhum cluster ECS encontrado")
            return

        print(f"✅ Total de clusters: {len(cluster_arns)}\n")

        for cluster_arn in cluster_arns:
            cluster_name = cluster_arn.split("/")[-1]
            print(f"\n🐳 Cluster: {cluster_name}")
            print(f"   ARN: {cluster_arn}")

            # Detalhes do cluster
            cluster_details = ecs.describe_clusters(clusters=[cluster_arn])
            if cluster_details["clusters"]:
                cluster = cluster_details["clusters"][0]
                print(f"   Status: {cluster['status']}")
                print(f"   Tasks ativas: {cluster.get('runningTasksCount', 0)}")
                print(f"   Tasks pendentes: {cluster.get('pendingTasksCount', 0)}")
                print(
                    f"   Container instances: {cluster.get('registeredContainerInstancesCount', 0)}"
                )

            # Listar services
            services = ecs.list_services(cluster=cluster_arn)
            service_arns = services.get("serviceArns", [])

            if service_arns:
                print(f"\n   📦 Services ({len(service_arns)}):")
                service_details = ecs.describe_services(
                    cluster=cluster_arn, services=service_arns
                )

                for service in service_details["services"]:
                    print(f"      - {service['serviceName']}")
                    print(
                        f"        Desired: {service['desiredCount']} | Running: {service['runningCount']}"
                    )
                    print(f"        Status: {service['status']}")

    except Exception as e:
        print(f"❌ Erro ao listar clusters ECS: {str(e)}")


def check_rds_instances(session):
    """Lista instâncias RDS (PostgreSQL)"""
    rds = session.client("rds")

    print("\n" + "=" * 80)
    print("INSTÂNCIAS RDS (PostgreSQL)")
    print("=" * 80)

    try:
        response = rds.describe_db_instances()
        instances = response.get("DBInstances", [])

        if not instances:
            print("❌ Nenhuma instância RDS encontrada")
            return

        print(f"✅ Total de instâncias: {len(instances)}\n")

        for instance in instances:
            print(f"\n🗄️  Instância: {instance['DBInstanceIdentifier']}")
            print(
                f"   Engine: {instance['Engine']} {instance.get('EngineVersion', '')}"
            )
            print(f"   Classe: {instance['DBInstanceClass']}")
            print(f"   Status: {instance['DBInstanceStatus']}")
            print(f"   Storage: {instance['AllocatedStorage']} GB")
            print(
                f"   Endpoint: {instance['Endpoint']['Address']}:{instance['Endpoint']['Port']}"
            )
            print(f"   Multi-AZ: {instance.get('MultiAZ', False)}")

            if instance.get("DBName"):
                print(f"   Database: {instance['DBName']}")

    except Exception as e:
        print(f"❌ Erro ao listar instâncias RDS: {str(e)}")


def main():
    """Função principal"""
    print("\n🔍 Verificando recursos AWS no perfil 'ysh-production'...")
    print("=" * 80)

    try:
        session = boto3.Session(profile_name="ysh-production")

        # Verificar credenciais
        sts = session.client("sts")
        identity = sts.get_caller_identity()
        print(f"\n✅ Autenticado como:")
        print(f"   Account: {identity['Account']}")
        print(f"   User/Role: {identity['Arn']}")

        # Verificar região
        region = session.region_name
        print(f"   Região: {region}")

        # Verificar recursos
        check_s3_buckets(session)
        check_ec2_instances(session)
        check_ecs_clusters(session)
        check_rds_instances(session)

        print("\n" + "=" * 80)
        print("✅ Verificação completa!")
        print("=" * 80 + "\n")

    except Exception as e:
        print(f"\n❌ Erro ao conectar com AWS: {str(e)}")
        print("\nDica: Execute 'aws sso login --profile ysh-production' primeiro")


if __name__ == "__main__":
    main()
