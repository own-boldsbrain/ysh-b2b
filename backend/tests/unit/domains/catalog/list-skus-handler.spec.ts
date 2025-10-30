import { ListSKUsHandler } from '../../../../src/domains/catalog/application/queries/handlers/list-skus-handler';
import { ListSKUsQuery } from '../../../../src/domains/catalog/application/queries/list-skus-query';
import { ProductSKU } from '../../../../src/domains/catalog/domain/entities/product-sku';

describe('ListSKUsHandler', () => {
  it('returns cached result when cache hit', async () => {
    const fakeCache = {
      get: jest.fn().mockResolvedValue({
        data: [{ id: 'sku-1', name: 'Test SKU', ysh_sku: 'YSH1', category: 'cat', average_price: { amount: 100, currency: 'BRL' }, is_active: true, created_at: new Date().toISOString(), updated_at: new Date().toISOString() }],
        pagination: { total: 1, limit: 20, offset: 0, hasMore: false }
      }),
      set: jest.fn()
    } as any;

    const fakeRepo = { listSKUs: jest.fn() } as any;
    const handler = new ListSKUsHandler(fakeRepo, fakeCache);

    const result = await handler.execute(new ListSKUsQuery({ page: 1, limit: 20 }));

    expect(fakeCache.get).toHaveBeenCalled();
    expect(result.data.length).toBe(1);
    expect(fakeRepo.listSKUs).not.toHaveBeenCalled();
  });

  it('queries repository and caches on miss', async () => {
    const sku = ProductSKU.fromPersistence({
      id: 'sku-2',
      ysh_sku: 'YSH2',
      name: 'SKU 2',
      category: 'cat',
      average_price: '100',
      is_active: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    });

    const fakeCache = {
      get: jest.fn().mockResolvedValue(null),
      set: jest.fn().mockResolvedValue(true)
    } as any;

    const fakeRepo = {
      listSKUs: jest.fn().mockResolvedValue({ data: [sku], pagination: { total: 1, limit: 20, offset: 0, hasMore: false } })
    } as any;

    const handler = new ListSKUsHandler(fakeRepo, fakeCache);
    const result = await handler.execute(new ListSKUsQuery({ page: 1, limit: 20 }));

    expect(fakeCache.get).toHaveBeenCalled();
    expect(fakeRepo.listSKUs).toHaveBeenCalled();
    expect(fakeCache.set).toHaveBeenCalled();
    expect(result.data.length).toBe(1);
  });
});
