"use client"

import * as React from "react"
import { useRouter } from "next/navigation"

import {
  Combobox,
  ComboboxChip,
  ComboboxChips,
  ComboboxChipsInput,
  ComboboxContent,
  ComboboxEmpty,
  ComboboxItem,
  ComboboxList,
  ComboboxValue,
  useComboboxAnchor,
} from "@/components/ui/combobox"

type ComboboxMultipleProps = {
  items: string[]
  selectedItems: string[]
  resultCount: number
  totalCount: number
}

export function ComboboxMultiple({
  items,
  selectedItems,
  resultCount,
  totalCount,
}: ComboboxMultipleProps) {
  const anchor = useComboboxAnchor()
  const router = useRouter()

  function updateCategories(values: string[]) {
    const searchParams = new URLSearchParams()

    values.forEach((value) => {
      searchParams.append("category", value)
    })

    const query = searchParams.toString()
    router.push(query ? `/news?${query}` : "/news")
  }

  return (
    <div className="grid w-full gap-2 sm:max-w-sm">
      <div className="flex items-center justify-between gap-3">
        <span className="text-xs font-medium uppercase text-muted-foreground">
          Category
        </span>
        <span className="text-sm text-muted-foreground">
          {resultCount} of {totalCount} stories
        </span>
      </div>
      <Combobox
        multiple
        autoHighlight
        items={items}
        value={selectedItems}
        onValueChange={updateCategories}
      >
        <ComboboxChips ref={anchor} className="w-full">
          <ComboboxValue>
            {(values) => (
              <React.Fragment>
                {values.map((value: string) => (
                  <ComboboxChip key={value}>{value}</ComboboxChip>
                ))}
                <ComboboxChipsInput placeholder={values.length ? "" : "All categories"} />
              </React.Fragment>
            )}
          </ComboboxValue>
        </ComboboxChips>
        <ComboboxContent anchor={anchor}>
          <ComboboxEmpty>No items found.</ComboboxEmpty>
          <ComboboxList>
            {(item) => (
              <ComboboxItem key={item} value={item}>
                {item}
              </ComboboxItem>
            )}
          </ComboboxList>
        </ComboboxContent>
      </Combobox>
    </div>
  )
}
