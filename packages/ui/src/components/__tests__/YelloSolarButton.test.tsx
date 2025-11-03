import * as React from "react"
import { render, screen } from "@testing-library/react"
import { YelloSolarButton } from "../yello-solar-button"

describe("YelloSolarButton", () => {
  it("should render correctly", () => {
    render(<YelloSolarButton>Click me</YelloSolarButton>)
    expect(screen.getByRole("button")).toHaveTextContent("Click me")
  })

  it("should forward a ref to the button element", () => {
    const ref = React.createRef<HTMLButtonElement>()
    render(<YelloSolarButton ref={ref}>Click me</YelloSolarButton>)
    expect(ref.current).toBeInstanceOf(HTMLButtonElement)
  })
})
