/**
 * Script para verificar e orientar sobre permissões necessárias
 */

import axios from 'axios';

const ACCESS_TOKEN = process.env.FACEBOOK_ACCESS_TOKEN || 'EAAUzVk5ZA6AMBPjdGQVd1IZCrIPZApjWxDhA6QzJFLvmyINn4rVUkqSvJKorbyYQRJL4KQS1RBYL7Fd3MKZAKjw8QILOhYTONoTRG3x0aZAtwgZCGo4uVfxQHZBGOhob3csZCKENZBfqoZAfIivhwZC8wcXHQ3HbI7rZAmZCMvI4fncjN3P1Cl8AXp3Xgu6zR4hhK1wZDZD';
const APP_ID = '1463820658272259';
const CATALOG_ID = '716960371408497';

async function checkPermissions() {
  console.log('🔍 Verificando permissões do token...\n');

  try {
    // Verificar token
    const debugResponse = await axios.get('https://graph.facebook.com/v21.0/debug_token', {
      params: {
        input_token: ACCESS_TOKEN,
        access_token: ACCESS_TOKEN
      }
    });

    const tokenInfo = debugResponse.data.data;
    const scopes = tokenInfo.scopes || [];

    console.log('📋 Permissões atuais:');
    scopes.forEach(scope => console.log(`   • ${scope}`));

    // Verificar permissões necessárias
    console.log('\n📋 Permissões necessárias para catálogo:');
    const requiredScopes = [
      'business_management',
      'catalog_management',
      'ads_management'
    ];

    const missingScopes = requiredScopes.filter(s => !scopes.includes(s));

    if (missingScopes.length > 0) {
      console.log('\n❌ Permissões faltando:');
      missingScopes.forEach(scope => console.log(`   ✗ ${scope}`));

      console.log('\n📋 COMO ADICIONAR PERMISSÕES:\n');
      console.log('1. Acesse o Graph API Explorer:');
      console.log('   https://developers.facebook.com/tools/explorer/\n');
      console.log('2. Selecione seu App "Yello Solar Hub" no topo\n');
      console.log('3. Clique em "Permissions" (Permissões)\n');
      console.log('4. Busque e adicione as seguintes permissões:');
      missingScopes.forEach(scope => console.log(`   ☐ ${scope}`));
      console.log('\n5. Clique em "Generate Access Token"\n');
      console.log('6. Copie o novo token e atualize no .env\n');

      console.log('═'.repeat(60));
      console.log('OU USE ESTE LINK DIRETO:');
      console.log('═'.repeat(60));
      
      const permissionsStr = requiredScopes.join(',');
      const explorerUrl = `https://developers.facebook.com/tools/explorer/?method=GET&path=me%3Ffields%3Did%2Cname&version=v21.0&app_id=${APP_ID}`;
      
      console.log(`\n${explorerUrl}\n`);
      console.log('Depois de gerar o token com as permissões, execute:');
      console.log('   node scripts/test-facebook-catalog.js\n');

      process.exit(1);
    }

    console.log('\n✅ Todas as permissões necessárias estão presentes!');

    // Tentar acessar catálogo
    console.log('\n🔍 Verificando acesso ao catálogo...');
    try {
      const catalogResponse = await axios.get(`https://graph.facebook.com/v21.0/${CATALOG_ID}`, {
        params: {
          access_token: ACCESS_TOKEN,
          fields: 'id,name,business'
        }
      });

      console.log('✅ Acesso ao catálogo OK!');
      console.log(`   Nome: ${catalogResponse.data.name}`);
      console.log('\n🎯 Pronto para sincronizar produtos!');

    } catch (error) {
      console.log('❌ Erro ao acessar catálogo:', error.response?.data?.error?.message);
      
      console.log('\n💡 SOLUÇÃO ALTERNATIVA:\n');
      console.log('Se você é admin do Business Manager, precisa:');
      console.log('1. Ir para Business Settings: https://business.facebook.com/settings/');
      console.log('2. Data Sources → Catalogs');
      console.log(`3. Selecionar o catálogo "${CATALOG_ID}"`);
      console.log('4. People → Assign Assets');
      console.log('5. Adicionar o System User com permissões completas\n');
    }

  } catch (error) {
    console.error('\n❌ Erro:', error.response?.data?.error?.message || error.message);
  }
}

checkPermissions();
