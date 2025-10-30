/**
 * Script para validar token de acesso do Facebook
 * Verifica permissões, validade e informações do app/usuário
 */

import axios from 'axios';

const ACCESS_TOKEN = process.env.FACEBOOK_ACCESS_TOKEN || 'EAAUzVk5ZA6AMBPjdGQVd1IZCrIPZApjWxDhA6QzJFLvmyINn4rVUkqSvJKorbyYQRJL4KQS1RBYL7Fd3MKZAKjw8QILOhYTONoTRG3x0aZAtwgZCGo4uVfxQHZBGOhob3csZCKENZBfqoZAfIivhwZC8wcXHQ3HbI7rZAmZCMvI4fncjN3P1Cl8AXp3Xgu6zR4hhK1wZDZD';

async function validateToken() {
  console.log('🔍 Validando token de acesso do Facebook...\n');

  try {
    // 1. Validar token e obter informações
    console.log('📊 Etapa 1: Validando token...');
    const debugResponse = await axios.get('https://graph.facebook.com/v21.0/debug_token', {
      params: {
        input_token: ACCESS_TOKEN,
        access_token: ACCESS_TOKEN
      }
    });

    const tokenInfo = debugResponse.data.data;
    console.log('✅ Token válido!\n');
    console.log('📋 Informações do Token:');
    console.log(`   App ID: ${tokenInfo.app_id}`);
    console.log(`   Tipo: ${tokenInfo.type}`);
    console.log(`   Válido: ${tokenInfo.is_valid}`);
    console.log(`   User ID: ${tokenInfo.user_id || 'N/A'}`);
    
    if (tokenInfo.expires_at) {
      const expiryDate = new Date(tokenInfo.expires_at * 1000);
      console.log(`   Expira em: ${expiryDate.toLocaleString('pt-BR')}`);
      const daysUntilExpiry = Math.floor((expiryDate - new Date()) / (1000 * 60 * 60 * 24));
      console.log(`   Dias restantes: ${daysUntilExpiry}`);
    } else {
      console.log(`   Expira em: Nunca (token permanente)`);
    }

    // 2. Verificar permissões
    console.log('\n📊 Etapa 2: Verificando permissões...');
    const scopes = tokenInfo.scopes || [];
    console.log(`   Permissões concedidas (${scopes.length}):`);
    
    const requiredScopes = [
      'catalog_management',
      'business_management',
      'pages_read_engagement',
      'pages_manage_metadata'
    ];

    const optionalScopes = [
      'instagram_basic',
      'instagram_shopping_tag_products',
      'whatsapp_business_management',
      'whatsapp_business_messaging'
    ];

    scopes.forEach(scope => {
      const isRequired = requiredScopes.includes(scope);
      const isOptional = optionalScopes.includes(scope);
      const marker = isRequired ? '✅' : isOptional ? '🟡' : '📌';
      console.log(`   ${marker} ${scope}`);
    });

    // Verificar permissões faltantes
    const missingRequired = requiredScopes.filter(s => !scopes.includes(s));
    if (missingRequired.length > 0) {
      console.log('\n⚠️  Permissões obrigatórias faltando:');
      missingRequired.forEach(scope => console.log(`   ❌ ${scope}`));
    }

    const missingOptional = optionalScopes.filter(s => !scopes.includes(s));
    if (missingOptional.length > 0) {
      console.log('\n💡 Permissões opcionais faltando (Instagram/WhatsApp):');
      missingOptional.forEach(scope => console.log(`   ⚪ ${scope}`));
    }

    // 3. Obter informações do usuário
    console.log('\n📊 Etapa 3: Informações do usuário...');
    try {
      const meResponse = await axios.get('https://graph.facebook.com/v21.0/me', {
        params: {
          access_token: ACCESS_TOKEN,
          fields: 'id,name,email'
        }
      });

      console.log(`   Nome: ${meResponse.data.name}`);
      console.log(`   ID: ${meResponse.data.id}`);
      console.log(`   Email: ${meResponse.data.email || 'N/A'}`);
    } catch (error) {
      console.log('   ⚠️  Não foi possível obter informações do usuário');
    }

    // 4. Tentar listar Business Accounts
    console.log('\n📊 Etapa 4: Verificando Business Accounts...');
    try {
      const businessResponse = await axios.get(`https://graph.facebook.com/v21.0/${tokenInfo.user_id}/businesses`, {
        params: {
          access_token: ACCESS_TOKEN,
          fields: 'id,name'
        }
      });

      if (businessResponse.data.data && businessResponse.data.data.length > 0) {
        console.log(`   ✅ ${businessResponse.data.data.length} Business Account(s) encontrada(s):`);
        businessResponse.data.data.forEach(business => {
          console.log(`      • ${business.name} (ID: ${business.id})`);
        });
      } else {
        console.log('   ⚠️  Nenhum Business Account encontrado');
      }
    } catch (error) {
      console.log('   ⚠️  Não foi possível listar Business Accounts');
      if (error.response?.data?.error) {
        console.log(`   Erro: ${error.response.data.error.message}`);
      }
    }

    // 5. Tentar listar catálogos
    console.log('\n📊 Etapa 5: Procurando catálogos...');
    try {
      const catalogsResponse = await axios.get(`https://graph.facebook.com/v21.0/${tokenInfo.user_id}/owned_product_catalogs`, {
        params: {
          access_token: ACCESS_TOKEN,
          fields: 'id,name,product_count,business'
        }
      });

      if (catalogsResponse.data.data && catalogsResponse.data.data.length > 0) {
        console.log(`   ✅ ${catalogsResponse.data.data.length} catálogo(s) encontrado(s):`);
        catalogsResponse.data.data.forEach(catalog => {
          console.log(`      • ${catalog.name}`);
          console.log(`        ID: ${catalog.id}`);
          console.log(`        Produtos: ${catalog.product_count || 0}`);
        });

        // Mostrar como configurar o .env
        const firstCatalog = catalogsResponse.data.data[0];
        console.log('\n💡 Adicione ao .env:');
        console.log(`FACEBOOK_CATALOG_ID=${firstCatalog.id}`);
      } else {
        console.log('   ⚠️  Nenhum catálogo encontrado');
        console.log('   💡 Crie um catálogo em: https://business.facebook.com/commerce');
      }
    } catch (error) {
      console.log('   ⚠️  Não foi possível listar catálogos');
      if (error.response?.data?.error) {
        console.log(`   Erro: ${error.response.data.error.message}`);
      }
    }

    // Resumo final
    console.log('\n' + '='.repeat(60));
    console.log('📋 RESUMO DA VALIDAÇÃO');
    console.log('='.repeat(60));
    
    const canUseFacebook = scopes.includes('catalog_management') || scopes.includes('business_management');
    const canUseInstagram = scopes.includes('instagram_basic');
    const canUseWhatsApp = scopes.includes('whatsapp_business_management');

    console.log(`✅ Token válido: SIM`);
    console.log(`📦 Facebook Catalog: ${canUseFacebook ? '✅ DISPONÍVEL' : '❌ FALTA PERMISSÃO'}`);
    console.log(`📱 Instagram Shopping: ${canUseInstagram ? '✅ DISPONÍVEL' : '⚪ NÃO CONFIGURADO'}`);
    console.log(`💬 WhatsApp Business: ${canUseWhatsApp ? '✅ DISPONÍVEL' : '⚪ NÃO CONFIGURADO'}`);
    
    if (!canUseFacebook) {
      console.log('\n⚠️  ATENÇÃO: Token não possui permissões para gerenciar catálogos!');
      console.log('   Solicite as seguintes permissões no Facebook App:');
      console.log('   • catalog_management');
      console.log('   • business_management');
    }

    console.log('\n🔐 Token para .env:');
    console.log(`FACEBOOK_ACCESS_TOKEN=${ACCESS_TOKEN}`);

  } catch (error) {
    console.error('\n❌ Erro ao validar token:');
    
    if (error.response) {
      console.error(`   Status: ${error.response.status}`);
      console.error(`   Mensagem: ${error.response.data?.error?.message || 'Erro desconhecido'}`);
      console.error(`   Tipo: ${error.response.data?.error?.type || 'N/A'}`);
      console.error(`   Code: ${error.response.data?.error?.code || 'N/A'}`);

      if (error.response.status === 190) {
        console.error('\n💡 Token inválido ou expirado. Gere um novo token em:');
        console.error('   https://developers.facebook.com/tools/explorer/');
      }
    } else {
      console.error(`   ${error.message}`);
    }
    
    process.exit(1);
  }
}

// Executar validação
validateToken();
