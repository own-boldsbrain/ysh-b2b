#!/usr/bin/env node
/**
 * Test RDS Connection via SSH Tunnel
 * Usage: node test-rds-connection.js
 */

import pkg from 'pg';
const { Client } = pkg;

const config = {
  host: '127.0.0.1',
  port: 59588,
  user: 'supabase_admin',
  password: 'po5lwIAe_kKb5Ham0nPr2qeah2CGDNys',
  database: 'postgres',
  ssl: { rejectUnauthorized: false }, // Túnel SSH + SSL requerido pelo RDS
  connectionTimeoutMillis: 10000,
};

console.log('🔌 Testando conexão com RDS via túnel SSH...');
console.log(`📍 Host: ${config.host}:${config.port}`);
console.log(`👤 User: ${config.user}`);
console.log(`🗄️  Database: ${config.database}\n`);

const client = new Client(config);

async function testConnection() {
  try {
    console.log('⏳ Conectando...');
    await client.connect();
    console.log('✅ Conexão estabelecida!\n');

    console.log('🔍 Executando queries de teste...\n');

    // Test 1: Current time
    const timeResult = await client.query('SELECT NOW() as current_time');
    console.log('✅ Test 1 - Current Time:');
    console.log(`   ${timeResult.rows[0].current_time}\n`);

    // Test 2: PostgreSQL version
    const versionResult = await client.query('SELECT version()');
    console.log('✅ Test 2 - PostgreSQL Version:');
    console.log(`   ${versionResult.rows[0].version}\n`);

    // Test 3: List databases
    const dbResult = await client.query(`
      SELECT datname, pg_size_pretty(pg_database_size(datname)) as size
      FROM pg_database
      WHERE datistemplate = false
      ORDER BY datname
    `);
    console.log('✅ Test 3 - Available Databases:');
    dbResult.rows.forEach(row => {
      console.log(`   📦 ${row.datname} (${row.size})`);
    });
    console.log();

    // Test 4: Connection info
    const connResult = await client.query(`
      SELECT 
        inet_server_addr() as server_ip,
        inet_server_port() as server_port,
        current_database() as current_db,
        current_user as current_user,
        pg_backend_pid() as backend_pid
    `);
    console.log('✅ Test 4 - Connection Info:');
    console.log(`   Server: ${connResult.rows[0].server_ip}:${connResult.rows[0].server_port}`);
    console.log(`   Database: ${connResult.rows[0].current_db}`);
    console.log(`   User: ${connResult.rows[0].current_user}`);
    console.log(`   Backend PID: ${connResult.rows[0].backend_pid}\n`);

    console.log('🎉 Todos os testes passaram! Túnel SSH → RDS está funcionando perfeitamente.\n');

  } catch (error) {
    console.error('❌ Erro na conexão:', error.message);
    console.error('\n🔍 Diagnóstico:');
    
    if (error.message.includes('ECONNREFUSED')) {
      console.error('   ⚠️  Túnel SSH não está ativo na porta 59588');
      console.error('   💡 Execute: ssh -vvv -i ".\\ysh-keypair.pem" -N -L 127.0.0.1:59588:ysh-b2b-production-supabase-db.cmxiy0wqok6l.us-east-1.rds.amazonaws.com:5432 ec2-user@34.234.100.225');
    } else if (error.message.includes('password authentication failed')) {
      console.error('   ⚠️  Senha incorreta ou usuário inválido');
      console.error('   💡 Verifique DATABASE_URL ou .env.aws');
    } else if (error.message.includes('timeout')) {
      console.error('   ⚠️  Timeout na conexão - possível problema de Security Group');
      console.error('   💡 Verifique se o SG do RDS permite acesso do bastion na porta 5432');
    } else {
      console.error('   ⚠️  Erro desconhecido:', error.stack);
    }
    
    process.exit(1);
  } finally {
    await client.end();
  }
}

testConnection();
