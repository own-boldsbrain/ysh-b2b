#!/usr/bin/env node

/**
 * Script para verificar schema da tabela DynamoDB
 */

import AWS from "aws-sdk";

const AWS_REGION = process.env.AWS_REGION || "us-east-1";
const DYNAMODB_TABLE = process.env.DYNAMODB_TABLE || "ysh-products-catalog";

async function checkDynamoDBSchema() {
  console.log("\n🔍 VERIFICANDO SCHEMA DA TABELA DYNAMODB\n");

  try {
    const dynamodb = new AWS.DynamoDB({ region: AWS_REGION });

    const tableInfo = await dynamodb
      .describeTable({ TableName: DYNAMODB_TABLE })
      .promise();

    console.log("📊 Informações da Tabela:\n");
    console.log(`Nome: ${tableInfo.Table.TableName}`);
    console.log(`Status: ${tableInfo.Table.TableStatus}`);
    console.log(`Item Count: ${tableInfo.Table.ItemCount}`);

    console.log("\n🔑 Key Schema:");
    tableInfo.Table.KeySchema.forEach((key) => {
      console.log(`   • ${key.AttributeName} (${key.KeyType})`);
    });

    console.log("\n📋 Attribute Definitions:");
    tableInfo.Table.AttributeDefinitions.forEach((attr) => {
      console.log(`   • ${attr.AttributeName}: ${attr.AttributeType}`);
    });

    if (tableInfo.Table.GlobalSecondaryIndexes) {
      console.log("\n🗂️  Global Secondary Indexes:");
      tableInfo.Table.GlobalSecondaryIndexes.forEach((gsi) => {
        console.log(`\n   Index: ${gsi.IndexName}`);
        gsi.KeySchema.forEach((key) => {
          console.log(`      • ${key.AttributeName} (${key.KeyType})`);
        });
      });
    }

    if (tableInfo.Table.LocalSecondaryIndexes) {
      console.log("\n📁 Local Secondary Indexes:");
      tableInfo.Table.LocalSecondaryIndexes.forEach((lsi) => {
        console.log(`\n   Index: ${lsi.IndexName}`);
        lsi.KeySchema.forEach((key) => {
          console.log(`      • ${key.AttributeName} (${key.KeyType})`);
        });
      });
    }

    console.log("\n");
  } catch (error) {
    console.error("❌ Erro:", error.message);
  }
}

checkDynamoDBSchema();
