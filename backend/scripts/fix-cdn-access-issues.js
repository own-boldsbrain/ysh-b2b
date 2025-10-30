import AWS from 'aws-sdk';

const s3 = new AWS.S3({ region: 'us-east-1' });
const cloudfront = new AWS.CloudFront();

const BUCKET_NAME = 'ysh-b2b-products';
const DISTRIBUTION_ID = 'E348HOJ6LS4HJO';

async function fixS3BucketPolicy() {
  console.log('\n🔧 Atualizando política do bucket S3...\n');
  
  const policy = {
    Version: '2012-10-17',
    Statement: [
      {
        Sid: 'PublicReadGetObject',
        Effect: 'Allow',
        Principal: '*',
        Action: 's3:GetObject',
        Resource: `arn:aws:s3:::${BUCKET_NAME}/images/*`
      }
    ]
  };
  
  try {
    await s3.putBucketPolicy({
      Bucket: BUCKET_NAME,
      Policy: JSON.stringify(policy)
    }).promise();
    
    console.log('✅ Política do bucket atualizada com sucesso!');
    console.log('   Permite: s3:GetObject em /images/*\n');
  } catch (error) {
    console.error('❌ Erro ao atualizar política:', error.message);
  }
}

async function addCloudfrontErrorPages() {
  console.log('🔧 Configurando páginas de erro no CloudFront...\n');
  
  try {
    // Obter configuração atual
    const { Distribution } = await cloudfront.getDistribution({
      Id: DISTRIBUTION_ID
    }).promise();
    
    const config = Distribution.DistributionConfig;
    const etag = Distribution.ETag;
    
    // Configurar páginas de erro customizadas
    config.CustomErrorResponses = {
      Quantity: 2,
      Items: [
        {
          ErrorCode: 403,
          ResponsePagePath: '',
          ResponseCode: '404',
          ErrorCachingMinTTL: 300
        },
        {
          ErrorCode: 404,
          ResponsePagePath: '',
          ResponseCode: '404',
          ErrorCachingMinTTL: 300
        }
      ]
    };
    
    // Atualizar distribuição
    await cloudfront.updateDistribution({
      Id: DISTRIBUTION_ID,
      DistributionConfig: config,
      IfMatch: etag
    }).promise();
    
    console.log('✅ Páginas de erro configuradas!');
    console.log('   403 → 404 (Access Denied retorna 404)');
    console.log('   404 → 404 (Not Found mantém 404)\n');
    
    console.log('⏳ Aguarde ~15-20min para deploy do CloudFront...\n');
  } catch (error) {
    console.error('❌ Erro ao configurar páginas de erro:', error.message);
  }
}

async function testCommonUrls() {
  console.log('🧪 Testando URLs comuns que podem gerar Access Denied...\n');
  
  const testUrls = [
    'https://cdn.yellosolarhub.com/',
    'https://cdn.yellosolarhub.com/products/',
    'https://cdn.yellosolarhub.com/products/inversores/',
    'https://cdn.yellosolarhub.com/products/inversores/nonexistent.png',
    'https://cdn.yellosolarhub.com/images/products/inversores/deye-sun-5k-g.webp',
    'https://cdn.yellosolarhub.com/products/inversores/deye-sun-5k-g.webp'
  ];
  
  for (const url of testUrls) {
    try {
      const response = await fetch(url, { method: 'HEAD' });
      const status = response.status === 200 ? '✅' : 
                     response.status === 404 ? '⚠️ ' : '❌';
      console.log(`${status} ${response.status} | ${url}`);
    } catch (error) {
      console.log(`❌ ERROR | ${url} | ${error.message}`);
    }
  }
  
  console.log('\n');
}

async function main() {
  console.log('\n🔧 CORREÇÃO DE PROBLEMAS DE ACESSO AO CDN');
  console.log('═'.repeat(70));
  
  await fixS3BucketPolicy();
  await addCloudfrontErrorPages();
  await testCommonUrls();
  
  console.log('═'.repeat(70));
  console.log('\n📋 PRÓXIMOS PASSOS:\n');
  console.log('1. ✅ Política S3 atualizada (efeito imediato)');
  console.log('2. ⏳ CloudFront em deploy (~15-20min)');
  console.log('3. 🧪 Após deploy, erros 403 retornarão 404\n');
  console.log('💡 URLs corretas sempre usam:');
  console.log('   https://cdn.yellosolarhub.com/products/[categoria]/[arquivo]\n');
}

main().catch(console.error);
