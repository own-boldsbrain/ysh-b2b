/*
  DynamoDB Browser Integration (ES module)
  - Uses AWS SDK v3 and Cognito Identity Pool to obtain temporary credentials
  - Exposes helper functions: createDynamoClient, getSKU, scanSKUs, putSKU

  Note: For production you must configure Cognito Identity Pool with minimal
  permissions and never grant excessive privileges to unauthenticated roles.
*/
import { CognitoIdentityClient } from "@aws-sdk/client-cognito-identity";
import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DynamoDBDocumentClient, GetCommand, ScanCommand, PutCommand } from "@aws-sdk/lib-dynamodb";
import { fromCognitoIdentityPool } from "@aws-sdk/credential-providers";

export async function createDynamoClient({ region = 'us-east-1', identityPoolId }) {
  if (!identityPoolId) throw new Error('identityPoolId is required');

  const creds = fromCognitoIdentityPool({
    client: new CognitoIdentityClient({ region }),
    identityPoolId
  });

  const client = new DynamoDBClient({ region, credentials: creds });
  const ddb = DynamoDBDocumentClient.from(client);

  const TABLE = 'ysh-products-catalog';

  return {
    async getSKU(skuKey) {
      if (!skuKey) throw new Error('skuKey is required');
      const cmd = new GetCommand({ TableName: TABLE, Key: { sku: skuKey } });
      const res = await ddb.send(cmd);
      return res.Item || null;
    },

    async scanSKUs({ limit = 100, exclusiveStartKey = undefined } = {}) {
      const cmd = new ScanCommand({ TableName: TABLE, Limit: limit, ExclusiveStartKey: exclusiveStartKey });
      const res = await ddb.send(cmd);
      return { items: res.Items || [], lastKey: res.LastEvaluatedKey };
    },

    async putSKU(item) {
      if (!item || typeof item !== 'object') throw new Error('item must be an object');
      if (!item.sku) throw new Error('item.sku is required');
      const cmd = new PutCommand({ TableName: TABLE, Item: item });
      const res = await ddb.send(cmd);
      return res;
    }
  };
}

// Usage example (ES module consumer):
// import { createDynamoClient } from './dynamodb-browser-integration.mjs';
// const client = await createDynamoClient({ region: 'us-east-1', identityPoolId: 'us-east-1:xxxx' });
// const sku = await client.getSKU('MY-SKU-001');
