/**
 * Script para testar conexão com o catálogo do Facebook
 * Cria um produto de teste e depois o deleta
 */

import axios from 'axios';

const ACCESS_TOKEN = process.env.FACEBOOK_ACCESS_TOKEN || 'EAAUzVk5ZA6AMBPjdGQVd1IZCrIPZApjWxDhA6QzJFLvmyINn4rVUkqSvJKorbyYQRJL4KQS1RBYL7Fd3MKZAKjw8QILOhYTONoTRG3x0aZAtwgZCGo4uVfxQHZBGOhob3csZCKENZBfqoZAfIivhwZC8wcXHQ3HbI7rZAmZCMvI4fncjN3P1Cl8AXp3Xgu6zR4hhK1wZDZD';
const CATALOG_ID = '716960371408497';

async function testCatalog() {
  console.log('🧪 Testando conexão com catálogo do Facebook...\n');
  console.log(`📦 Catalog ID: ${CATALOG_ID}\n`);

  try {
    // 1. Verificar acesso ao catálogo
    console.log('📊 Etapa 1: Verificando acesso ao catálogo...');
    const catalogResponse = await axios.get(`https://graph.facebook.com/v21.0/${CATALOG_ID}`, {
      params: {
        access_token: ACCESS_TOKEN,
        fields: 'id,name,product_count,business,vertical'
      }
    });

    const catalog = catalogResponse.data;
    console.log('✅ Catálogo acessado com sucesso!');
    console.log(`   Nome: ${catalog.name}`);
    console.log(`   Produtos: ${catalog.product_count || 0}`);
    console.log(`   Vertical: ${catalog.vertical || 'N/A'}`);
    if (catalog.business) {
      console.log(`   Business: ${catalog.business.name || catalog.business.id}`);
    }

    // 2. Criar produto de teste
    console.log('\n📊 Etapa 2: Criando produto de teste...');
    const testProduct = {
      retailer_id: `TEST_${Date.now()}`,
      name: 'Produto de Teste YSH - Painel Solar 550W',
      description: 'Este é um produto de teste da integração YSH Solar Hub com Facebook Catalog',
      availability: 'in stock',
      condition: 'new',
      price: 150000, // Em centavos (1500.00 BRL)
      currency: 'BRL',
      url: 'https://yellosolarhub.com/test-product',
      image_url: 'https://via.placeholder.com/800x600/FFD700/000000?text=YSH+Solar+550W',
      brand: 'YSH Solar',
      google_product_category: 1279 // Home & Garden > Pool & Spa > Solar Pool Heating
    };

    const createResponse = await axios.post(
      `https://graph.facebook.com/v21.0/${CATALOG_ID}/products`,
      testProduct,
      {
        params: { access_token: ACCESS_TOKEN }
      }
    );

    const productId = createResponse.data.id;
    console.log('✅ Produto de teste criado!');
    console.log(`   Product ID: ${productId}`);
    console.log(`   Retailer ID: ${testProduct.retailer_id}`);

    // 3. Verificar produto criado
    console.log('\n📊 Etapa 3: Verificando produto criado...');
    const productResponse = await axios.get(`https://graph.facebook.com/v21.0/${productId}`, {
      params: {
        access_token: ACCESS_TOKEN,
        fields: 'id,retailer_id,name,price,availability,url'
      }
    });

    console.log('✅ Produto verificado:');
    console.log(`   Nome: ${productResponse.data.name}`);
    console.log(`   Preço: ${productResponse.data.price}`);
    console.log(`   Disponibilidade: ${productResponse.data.availability}`);

    // 4. Atualizar produto
    console.log('\n📊 Etapa 4: Atualizando produto de teste...');
    await axios.post(
      `https://graph.facebook.com/v21.0/${productId}`,
      {
        price: 165000, // 1650.00 BRL em centavos
        availability: 'available for order'
      },
      {
        params: { access_token: ACCESS_TOKEN }
      }
    );
    console.log('✅ Produto atualizado com sucesso!');

    // 5. Deletar produto de teste
    console.log('\n📊 Etapa 5: Deletando produto de teste...');
    await axios.delete(`https://graph.facebook.com/v21.0/${productId}`, {
      params: { access_token: ACCESS_TOKEN }
    });
    console.log('✅ Produto de teste deletado!');

    // 6. Verificar contagem de produtos
    console.log('\n📊 Etapa 6: Verificando estado final do catálogo...');
    const finalCatalogResponse = await axios.get(`https://graph.facebook.com/v21.0/${CATALOG_ID}`, {
      params: {
        access_token: ACCESS_TOKEN,
        fields: 'id,name,product_count'
      }
    });

    console.log(`✅ Produtos no catálogo: ${finalCatalogResponse.data.product_count || 0}`);

    // Resumo
    console.log('\n' + '='.repeat(60));
    console.log('✅ TESTE COMPLETO - TUDO FUNCIONANDO!');
    console.log('='.repeat(60));
    console.log('\n📋 Operações testadas:');
    console.log('   ✅ Acesso ao catálogo');
    console.log('   ✅ Criar produto');
    console.log('   ✅ Ler produto');
    console.log('   ✅ Atualizar produto');
    console.log('   ✅ Deletar produto');
    console.log('\n🎯 Próximo passo:');
    console.log('   Execute o sync completo dos produtos YSH:');
    console.log('   POST /admin/facebook-catalog/sync\n');

  } catch (error) {
    console.error('\n❌ Erro durante o teste:');
    
    if (error.response) {
      console.error(`   Status: ${error.response.status}`);
      console.error(`   Mensagem: ${error.response.data?.error?.message || 'Erro desconhecido'}`);
      console.error(`   Tipo: ${error.response.data?.error?.type || 'N/A'}`);
      console.error(`   Code: ${error.response.data?.error?.code || 'N/A'}`);

      if (error.response.data?.error?.error_user_msg) {
        console.error(`   Detalhe: ${error.response.data.error.error_user_msg}`);
      }

      if (error.response.status === 403) {
        console.error('\n💡 Possível problema de permissões.');
        console.error('   Verifique que o token tem permissão "catalog_management"');
        console.error('   Execute: node scripts/validate-facebook-token.js');
      }

      if (error.response.status === 190) {
        console.error('\n💡 Token inválido ou expirado.');
        console.error('   Gere um novo token em: https://developers.facebook.com/tools/explorer/');
      }
    } else {
      console.error(`   ${error.message}`);
    }
    
    process.exit(1);
  }
}

testCatalog();
