import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Lista de imagens sincronizadas recentemente
const recentlySyncedImages = [
  // GOODWE (20)
  'goodwe-gw-10k-ms-30-20a-afci.png',
  'goodwe-gw-12klv-mt.jpg',
  'goodwe-gw-12klv-sdt-c30-afci.png',
  'goodwe-gw-15klv-mt.jpeg',
  'goodwe-gw-20klv-mt-afci.png',
  'goodwe-gw-30k-sdt-c30-afci.png',
  'goodwe-gw-3300-xs-30-afci.png',
  'goodwe-gw-35kls-mt-afci.png',
  'goodwe-gw-36k-mt-afci.jpeg',
  'goodwe-gw-5000-dns-30-16a-afci.png',
  'goodwe-gw-50ks-mt-afci.png',
  'goodwe-gw-60ks-mt-afci.png',
  'goodwe-gw-60ks-mt.png',
  'goodwe-gw-73klv-ht-afci.png',
  'goodwe-gw10k-bt.webp',
  'goodwe-gw250kn-ht.png',
  'goodwe-gw3600-es-br20-afci.png',
  'goodwe-gw6000-es-br20-afci.png',
  'goodwe-gw6000-sbp-20.webp',
  'goodwe-ezlogger-pro.png',
  // DEYE (5)
  'deye-sun-25k-g02-lv.png',
  'deye-sun-35k-g02-lv.jpeg',
  'deye-sun-5k-g.webp',
  'deye-sun-75k-g01p3-lv.png',
  'deye-sun-8k-g.jpg',
  // HUAWEI (5)
  'huawei-sun2000-10k-lc0-afci.png',
  'huawei-sun2000-12k-mb0-afci.png',
  'huawei-sun2000-15k-mb0-afci.png',
  'huawei-sun2000-3ktl-l1-afci.png',
  'huawei-sun2000-4ktl-l1-afci.png',
  // GROWATT (4)
  'growatt-mac-36ktl3-xl-afci.png',
  'growatt-max-50ktl3-xl2-afci.png',
  'growatt-mid-20ktl3-xl2-afci.png',
  'growatt-mid-50ktl3-x2-afci.png',
  // ENPHASE (1)
  'enphase-iq8p-72-2-br.jpeg'
];

async function testImageAccess(filename) {
  const url = `https://cdn.yellosolarhub.com/products/inversores/${filename}`;
  
  try {
    const response = await fetch(url, { method: 'HEAD' });
    
    if (response.ok) {
      return { filename, url, status: response.status, success: true };
    } else {
      return { 
        filename, 
        url, 
        status: response.status, 
        success: false,
        error: `HTTP ${response.status}`
      };
    }
  } catch (error) {
    return { 
      filename, 
      url, 
      status: 'ERROR', 
      success: false,
      error: error.message
    };
  }
}

async function testAllImages() {
  console.log('\n🔍 Testando acesso às 35 imagens sincronizadas...\n');
  console.log('═'.repeat(70));
  
  const results = {
    success: [],
    failed: [],
    total: recentlySyncedImages.length
  };
  
  for (const filename of recentlySyncedImages) {
    const result = await testImageAccess(filename);
    
    if (result.success) {
      results.success.push(result);
      console.log(`✅ ${filename.padEnd(40)} | ${result.status}`);
    } else {
      results.failed.push(result);
      console.log(`❌ ${filename.padEnd(40)} | ${result.error}`);
    }
    
    // Pequeno delay para não sobrecarregar
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  
  console.log('\n' + '═'.repeat(70));
  console.log(`\n📊 RESULTADO FINAL\n`);
  console.log(`   Total testado: ${results.total}`);
  console.log(`   ✅ Sucesso: ${results.success.length}`);
  console.log(`   ❌ Falha: ${results.failed.length}`);
  
  if (results.failed.length > 0) {
    console.log(`\n❌ IMAGENS COM ERRO:\n`);
    results.failed.forEach(item => {
      console.log(`   ${item.filename}`);
      console.log(`   URL: ${item.url}`);
      console.log(`   Erro: ${item.error}\n`);
    });
  } else {
    console.log(`\n✨ Todas as 35 imagens estão acessíveis via CDN!\n`);
  }
  
  console.log('═'.repeat(70) + '\n');
}

testAllImages().catch(console.error);
