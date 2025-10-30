/**
 * Script para buscar catálogos disponíveis no Facebook Commerce
 */

import axios from 'axios';

const ACCESS_TOKEN = process.env.FACEBOOK_ACCESS_TOKEN || 'EAAUzVk5ZA6AMBPjdGQVd1IZCrIPZApjWxDhA6QzJFLvmyINn4rVUkqSvJKorbyYQRJL4KQS1RBYL7Fd3MKZAKjw8QILOhYTONoTRG3x0aZAtwgZCGo4uVfxQHZBGOhob3csZCKENZBfqoZAfIivhwZC8wcXHQ3HbI7rZAmZCMvI4fncjN3P1Cl8AXp3Xgu6zR4hhK1wZDZD';
const SYSTEM_USER_ID = '122096690757086102'; // Do token validation

async function findCatalogs() {
  console.log('🔍 Buscando catálogos do Facebook Commerce...\n');

  try {
    // Método 1: Via system user
    console.log('📊 Método 1: Via System User...');
    try {
      const response = await axios.get(`https://graph.facebook.com/v21.0/${SYSTEM_USER_ID}/owned_product_catalogs`, {
        params: {
          access_token: ACCESS_TOKEN,
          fields: 'id,name,product_count,business'
        }
      });

      if (response.data.data && response.data.data.length > 0) {
        console.log(`✅ ${response.data.data.length} catálogo(s) encontrado(s):\n`);
        response.data.data.forEach((catalog, index) => {
          console.log(`${index + 1}. ${catalog.name}`);
          console.log(`   ID: ${catalog.id}`);
          console.log(`   Produtos: ${catalog.product_count || 0}`);
          if (catalog.business) {
            console.log(`   Business: ${catalog.business.name} (${catalog.business.id})`);
          }
          console.log('');
        });
        return response.data.data;
      }
    } catch (error) {
      console.log('⚠️  Método 1 falhou:', error.response?.data?.error?.message || error.message);
    }

    // Método 2: Buscar via business
    console.log('\n📊 Método 2: Buscando via Business Manager...');
    try {
      const businessResponse = await axios.get('https://graph.facebook.com/v21.0/me/businesses', {
        params: {
          access_token: ACCESS_TOKEN,
          fields: 'id,name'
        }
      });

      if (businessResponse.data.data && businessResponse.data.data.length > 0) {
        console.log(`✅ ${businessResponse.data.data.length} business(es) encontrado(s)\n`);
        
        for (const business of businessResponse.data.data) {
          console.log(`Business: ${business.name} (${business.id})`);
          
          try {
            const catalogsResponse = await axios.get(`https://graph.facebook.com/v21.0/${business.id}/owned_product_catalogs`, {
              params: {
                access_token: ACCESS_TOKEN,
                fields: 'id,name,product_count'
              }
            });

            if (catalogsResponse.data.data && catalogsResponse.data.data.length > 0) {
              console.log(`   ✅ ${catalogsResponse.data.data.length} catálogo(s):\n`);
              catalogsResponse.data.data.forEach(catalog => {
                console.log(`   • ${catalog.name}`);
                console.log(`     ID: ${catalog.id}`);
                console.log(`     Produtos: ${catalog.product_count || 0}\n`);
              });
              return catalogsResponse.data.data;
            } else {
              console.log('   ⚠️  Nenhum catálogo encontrado\n');
            }
          } catch (error) {
            console.log(`   ⚠️  Erro ao buscar catálogos: ${error.response?.data?.error?.message || error.message}\n`);
          }
        }
      }
    } catch (error) {
      console.log('⚠️  Método 2 falhou:', error.response?.data?.error?.message || error.message);
    }

    // Método 3: Buscar via app
    console.log('\n📊 Método 3: Buscando via App ID...');
    const APP_ID = '1463820658272259'; // Do token validation
    
    try {
      const appResponse = await axios.get(`https://graph.facebook.com/v21.0/${APP_ID}/product_catalogs`, {
        params: {
          access_token: ACCESS_TOKEN,
          fields: 'id,name,product_count,business'
        }
      });

      if (appResponse.data.data && appResponse.data.data.length > 0) {
        console.log(`✅ ${appResponse.data.data.length} catálogo(s) encontrado(s):\n`);
        appResponse.data.data.forEach((catalog, index) => {
          console.log(`${index + 1}. ${catalog.name}`);
          console.log(`   ID: ${catalog.id}`);
          console.log(`   Produtos: ${catalog.product_count || 0}`);
          if (catalog.business) {
            console.log(`   Business: ${catalog.business.name || catalog.business.id}`);
          }
          console.log('');
        });
        return appResponse.data.data;
      } else {
        console.log('⚠️  Nenhum catálogo encontrado via app');
      }
    } catch (error) {
      console.log('⚠️  Método 3 falhou:', error.response?.data?.error?.message || error.message);
    }

    // Método 4: Tentativa direta de listar sem especificar dono
    console.log('\n📊 Método 4: Busca genérica...');
    try {
      const searchResponse = await axios.get('https://graph.facebook.com/v21.0/search', {
        params: {
          access_token: ACCESS_TOKEN,
          type: 'product_catalog',
          q: 'catalog'
        }
      });

      if (searchResponse.data.data && searchResponse.data.data.length > 0) {
        console.log(`✅ ${searchResponse.data.data.length} resultado(s):\n`);
        searchResponse.data.data.forEach(item => {
          console.log(`   • ID: ${item.id}`);
        });
        return searchResponse.data.data;
      }
    } catch (error) {
      console.log('⚠️  Método 4 falhou:', error.response?.data?.error?.message || error.message);
    }

    console.log('\n❌ Nenhum catálogo encontrado por nenhum método.');
    console.log('\n💡 Para criar um catálogo:');
    console.log('   1. Acesse: https://business.facebook.com/commerce');
    console.log('   2. Vá em "Catálogos" → "Criar Catálogo"');
    console.log('   3. Escolha "E-commerce"');
    console.log('   4. Copie o Catalog ID gerado\n');

  } catch (error) {
    console.error('\n❌ Erro ao buscar catálogos:');
    console.error(`   ${error.message}`);
    if (error.response?.data) {
      console.error(`   Detalhes:`, error.response.data);
    }
  }
}

findCatalogs();
