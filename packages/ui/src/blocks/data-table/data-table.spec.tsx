import { act, renderHook } from "@testing-library/react"
import { useDataTable } from "./use-data-table"

const MOCK_DATA = [
  { id: "1", name: "John Doe", email: "john@test.com" },
  { id: "2", name: "Jane Doe", email: "jane@test.com" },
]

const MOCK_COLUMNS = [
  { accessorKey: "name", header: "Name" },
  { accessorKey: "email", header: "Email" },
]

describe("useDataTable", () => {
  it("should return the correct initial state", () => {
    const { result } = renderHook(() =>
      useDataTable({
        data: MOCK_DATA,
        columns: MOCK_COLUMNS,
      })
    )

    expect(result.current.getRowModel().rows).toHaveLength(2)
    expect(result.current.getSorting()).toBeNull()
    expect(result.current.getFiltering()).toEqual({})
    expect(result.current.getSearch()).toBe("")
    expect(result.current.pageIndex).toBe(0)
    expect(result.current.pageSize).toBe(10)
  })

  it("should handle sorting changes", () => {
    let sortingState = null
    const onSortingChange = jest.fn((newState) => {
      sortingState = newState
    })

    const { result, rerender } = renderHook(
      (props) =>
        useDataTable({
          data: MOCK_DATA,
          columns: MOCK_COLUMNS,
          sorting: {
            state: props.sorting,
            onSortingChange,
          },
        }),
      {
        initialProps: { sorting: sortingState },
      }
    )

    act(() => {
      result.current.setSorting({ id: "name", desc: false })
    })

    rerender({ sorting: sortingState })

    expect(onSortingChange).toHaveBeenCalledWith({ id: "name", desc: false })
    expect(result.current.getSorting()).toEqual({ id: "name", desc: false })
  })

  it("should handle filtering changes", () => {
    const onFilteringChange = jest.fn()
    const { result } = renderHook(() =>
      useDataTable({
        data: MOCK_DATA,
        columns: MOCK_COLUMNS,
        filtering: {
          state: {},
          onFilteringChange,
        },
      })
    )

    act(() => {
      result.current.addFilter({ id: "name", value: "John" })
    })

    expect(onFilteringChange).toHaveBeenCalledWith({ name: "John" })

    act(() => {
      result.current.removeFilter("name")
    })

    expect(onFilteringChange).toHaveBeenCalledWith({})
  })

  it("should handle pagination changes", () => {
    const onPaginationChange = jest.fn()
    const { result } = renderHook(() =>
      useDataTable({
        data: MOCK_DATA,
        columns: MOCK_COLUMNS,
        pagination: {
          state: { pageIndex: 0, pageSize: 1 },
          onPaginationChange,
        },
      })
    )

    expect(result.current.getRowModel().rows).toHaveLength(2)

    act(() => {
      result.current.nextPage()
    })

    expect(onPaginationChange).toHaveBeenCalledWith({
      pageIndex: 1,
      pageSize: 1,
    })
  })
})
