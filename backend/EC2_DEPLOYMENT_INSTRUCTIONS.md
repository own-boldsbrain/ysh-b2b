# EC2 Deployment Instructions - YSH Backend

## ✅ Completed Steps

1. **Docker Build**: ✅ Image `ysh-backend:latest` built successfully
2. **ECR Push**: ✅ Image pushed to `773235999227.dkr.ecr.us-east-1.amazonaws.com/ysh-backend:latest`
3. **Database Migration**: ✅ 003-create-catalog-table.sql executed on RDS
4. **Catalog Import**: ✅ 574 products imported (R$ 2.8M)

## 🎯 Next Steps: EC2 Deployment

### Infrastructure Overview
- **Architecture**: EC2 instances (não ECS/Fargate)
- **Backend Instance**: i-009c1d9c4dd119508 (18.204.214.68)
- **Key Pair**: medusa_db
- **Security Group**: production-ysh-stack-BackendSecurityGroup-ReZlXFPxReCM

### Deployment Method: SSH + Docker Pull

#### 1. Connect to EC2 Instance
```powershell
# Get SSH key from AWS Secrets Manager or local key storage
ssh -i path/to/medusa_db.pem ec2-user@18.204.214.68
```

#### 2. Pull New Image
```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 773235999227.dkr.ecr.us-east-1.amazonaws.com

# Pull latest image
docker pull 773235999227.dkr.ecr.us-east-1.amazonaws.com/ysh-backend:latest
```

#### 3. Stop Current Container
```bash
# Find running container
docker ps | grep ysh-backend

# Stop gracefully (replace CONTAINER_ID)
docker stop <CONTAINER_ID>

# Or stop all backend containers
docker stop $(docker ps -q --filter "ancestor=773235999227.dkr.ecr.us-east-1.amazonaws.com/ysh-backend")
```

#### 4. Start New Container
```bash
# Run with production environment
docker run -d \
  --name ysh-backend \
  --restart unless-stopped \
  -p 9000:9000 \
  -p 9001:9001 \
  -e DATABASE_URL="postgresql://supabase_admin:po5lwIAe_kKb5Ham0nPr2qeah2CGDNys@ysh-b2b-production-supabase-db.cmxiy0wqok6l.us-east-1.rds.amazonaws.com:5432/postgres?sslmode=require" \
  -e NODE_ENV=production \
  773235999227.dkr.ecr.us-east-1.amazonaws.com/ysh-backend:latest
```

**Note**: Adjust environment variables based on actual .env.production configuration.

#### 5. Verify Deployment
```bash
# Check logs
docker logs -f ysh-backend

# Verify health
curl http://localhost:9000/health

# Check catalog API
curl http://localhost:9000/store/catalog/skus | jq '.skus | length'
```

#### 6. Cleanup Old Images (Optional)
```bash
# Remove old images to free disk space
docker image prune -a -f
```

## 🔍 Validation Queries

### Test Catalog Integration
```bash
# On EC2 instance
curl http://localhost:9000/store/catalog/skus?limit=10 | jq '.'

# Check product count
curl http://localhost:9000/store/catalog/skus | jq '.skus | length'

# Test specific SKU
curl http://localhost:9000/store/catalog/skus/JINKO-JKM575N-72HL4-BDV | jq '.'
```

### Database Validation (from bastion)
```sql
-- Connect via SSH tunnel
psql "postgresql://supabase_admin:po5lwIAe_kKb5Ham0nPr2qeah2CGDNys@127.0.0.1:59588/postgres?sslmode=require"

-- Check imported products
SELECT category, COUNT(*) as products, SUM(price) as total_value
FROM catalog 
WHERE is_active = true
GROUP BY category
ORDER BY total_value DESC;

-- Verify indexes
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'catalog';
```

## 🚨 Troubleshooting

### Container Fails to Start
```bash
# Check logs for errors
docker logs ysh-backend

# Common issues:
# 1. Database connection: Verify DATABASE_URL and RDS security group
# 2. Port conflict: Ensure ports 9000/9001 are not in use
# 3. Memory: Check available memory with 'free -h'
```

### Health Check Fails
```bash
# Test internal health endpoint
docker exec ysh-backend curl http://localhost:9000/health

# Check if migrations ran
docker exec ysh-backend npm run migration:show
```

### Catalog API Returns Empty
```bash
# Verify database connection from container
docker exec ysh-backend node -e "
const { Pool } = require('pg');
const pool = new Pool({ connectionString: process.env.DATABASE_URL });
pool.query('SELECT COUNT(*) FROM catalog').then(r => console.log(r.rows));
"
```

## 📊 Monitoring

### CloudWatch Logs (if configured)
```powershell
aws logs tail /aws/ec2/ysh-backend --follow --region us-east-1
```

### Container Stats
```bash
# On EC2
docker stats ysh-backend
```

## 🔄 Rollback Procedure

If deployment fails:

```bash
# Stop new container
docker stop ysh-backend
docker rm ysh-backend

# Find previous working image
docker images | grep ysh-backend

# Restart with previous image tag
docker run -d \
  --name ysh-backend \
  --restart unless-stopped \
  -p 9000:9000 \
  -p 9001:9001 \
  -e DATABASE_URL="..." \
  773235999227.dkr.ecr.us-east-1.amazonaws.com/ysh-backend:<PREVIOUS_TAG>
```

## 📝 Post-Deployment Checklist

- [ ] Container running (`docker ps`)
- [ ] Health check passing (`curl localhost:9000/health`)
- [ ] Catalog API returning 574 products
- [ ] Logs show no errors (`docker logs ysh-backend`)
- [ ] Public endpoint accessible (if load balancer configured)
- [ ] Monitoring alerts configured

## 🔗 Related Documentation

- **RDS Connection**: AWS_RDS_CONNECTION_SETUP.md
- **Migration Scripts**: scripts/run-rds-migration.js
- **Import Results**: 574/1138 products, 20 categories, 14 manufacturers
- **CloudFormation**: ysh-b2b-production stack

---

**Status**: Image ready in ECR, awaiting EC2 SSH deployment
**Next Action**: SSH into i-009c1d9c4dd119508 and execute deployment steps
