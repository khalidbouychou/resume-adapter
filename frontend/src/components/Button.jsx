import * as React from "react"
import { cn } from "../lib/utils"

const Button = React.forwardRef(({ className, variant = "default", size = "default", disabled, ...props }, ref) => {
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2",
        "disabled:pointer-events-none disabled:opacity-50",
        {
          "bg-black text-white hover:bg-gray-800": variant === "default",
          "border border-gray-300 bg-white hover:bg-gray-50": variant === "outline",
        },
        {
          "h-10 px-4 py-2": size === "default",
          "h-9 px-3": size === "sm",
          "h-11 px-8": size === "lg",
        },
        className
      )}
      ref={ref}
      disabled={disabled}
      {...props}
    />
  )
})

Button.displayName = "Button"

export { Button }
