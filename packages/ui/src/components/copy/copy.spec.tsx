import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import * as React from "react"
import { TooltipProvider } from "../tooltip"
import { Copy } from "./copy"

jest.mock("copy-to-clipboard", () => jest.fn())

describe("Copy", () => {
  it("should render", () => {
    render(
      <TooltipProvider>
        <Copy content="Hello world" />
      </TooltipProvider>
    )
    expect(screen.getByRole("button")).toBeInTheDocument()
  })
  it("should copy to clipboard when clicked", async () => {
    const user = userEvent.setup()
    const onCopy = jest.fn()
    render(
      <TooltipProvider>
        <Copy content="Hello world" onCopy={onCopy} />
      </TooltipProvider>
    )
    const button = screen.getByRole("button")
    await user.click(button)
    expect(onCopy).toHaveBeenCalledTimes(1)
  })
})
