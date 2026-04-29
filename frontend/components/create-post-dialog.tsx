"use client"

import React from "react"
import { z } from "zod"

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "./ui/dialog"
import { Button } from "./ui/button"
import { Input } from "./ui/input"
import { Label } from "./ui/label"
import { Textarea } from "./ui/textarea"

const createPostSchema = z.object({
  title: z
    .string()
    .trim()
    .min(3, "Title must be at least 3 characters.")
    .max(120, "Title must be 120 characters or fewer."),
  category: z
    .string()
    .trim()
    .min(2, "Category must be at least 2 characters.")
    .max(40, "Category must be 40 characters or fewer."),
  body: z
    .string()
    .trim()
    .min(20, "Body must be at least 20 characters.")
    .max(5000, "Body must be 5,000 characters or fewer."),
  date: z.string().min(1, "Date is required."),
})

type CreatePostForm = z.infer<typeof createPostSchema>
type CreatePostErrors = Partial<Record<keyof CreatePostForm, string>>

const defaultFormValues: Omit<CreatePostForm, "date"> = {
  title: "",
  category: "",
  body: "",
}

function formatPostDate(date: Date) {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(date)
}

const CreatePostDialog = () => {
  const [formValues, setFormValues] = React.useState(defaultFormValues)
  const [errors, setErrors] = React.useState<CreatePostErrors>({})
  const [submittedPost, setSubmittedPost] = React.useState<CreatePostForm | null>(
    null
  )

  const currentDate = formatPostDate(new Date())

  function updateField<Field extends keyof typeof defaultFormValues>(
    field: Field,
    value: (typeof defaultFormValues)[Field]
  ) {
    setFormValues((current) => ({ ...current, [field]: value }))
    setErrors((current) => ({ ...current, [field]: undefined }))
  }

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()

    const result = createPostSchema.safeParse({
      ...formValues,
      date: currentDate,
    })

    if (!result.success) {
      const fieldErrors = result.error.flatten().fieldErrors

      setErrors({
        title: fieldErrors.title?.[0],
        category: fieldErrors.category?.[0],
        body: fieldErrors.body?.[0],
        date: fieldErrors.date?.[0],
      })
      setSubmittedPost(null)
      return
    }

    setSubmittedPost(result.data)
    setErrors({})
    setFormValues(defaultFormValues)
  }

  return (
    <Dialog>
      <DialogTrigger
        render={
          <Button
            variant="ghost"
            size="sm"
            className="text-muted-foreground hover:text-foreground"
          >
            Create new
          </Button>
        }
      />
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Create post</DialogTitle>
          <DialogDescription>
            Add a new post with today&apos;s date applied automatically.
          </DialogDescription>
        </DialogHeader>

        <form className="grid gap-4" onSubmit={handleSubmit} noValidate>
          <div className="grid gap-2">
            <Label htmlFor="post-title">Title</Label>
            <Input
              id="post-title"
              name="title"
              value={formValues.title}
              onChange={(event) => updateField("title", event.target.value)}
              aria-invalid={Boolean(errors.title)}
              aria-describedby={errors.title ? "post-title-error" : undefined}
              placeholder="Enter post title"
            />
            {errors.title && (
              <p id="post-title-error" className="text-xs text-destructive">
                {errors.title}
              </p>
            )}
          </div>

          <div className="grid gap-2">
            <Label htmlFor="post-category">Category</Label>
            <Input
              id="post-category"
              name="category"
              value={formValues.category}
              onChange={(event) => updateField("category", event.target.value)}
              aria-invalid={Boolean(errors.category)}
              aria-describedby={
                errors.category ? "post-category-error" : undefined
              }
              placeholder="Business"
            />
            {errors.category && (
              <p id="post-category-error" className="text-xs text-destructive">
                {errors.category}
              </p>
            )}
          </div>

          <div className="grid gap-2">
            <Label htmlFor="post-body">Body</Label>
            <Textarea
              id="post-body"
              name="body"
              value={formValues.body}
              onChange={(event) => updateField("body", event.target.value)}
              aria-invalid={Boolean(errors.body)}
              aria-describedby={errors.body ? "post-body-error" : undefined}
              className="min-h-32"
              placeholder="Write the post body"
            />
            {errors.body && (
              <p id="post-body-error" className="text-xs text-destructive">
                {errors.body}
              </p>
            )}
          </div>

          {submittedPost && (
            <p className="rounded-lg bg-muted px-3 py-2 text-xs text-muted-foreground">
              Post validated for {submittedPost.date}.
            </p>
          )}

          <DialogFooter>
            <Button type="submit">Create post</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

export default CreatePostDialog
