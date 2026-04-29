import Link from "next/link";
import { ArrowUpRight, FileText, Users } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { newsItems } from "@/lib/news";

export default function AdminPage() {
  const publishedCount = newsItems.filter((item) => item.status === "Published").length;

  return (
    <div className="mx-auto flex w-full max-w-7xl flex-1 flex-col gap-8 px-4 py-10 sm:px-6 lg:px-8">
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
        <div>
          <Badge variant="secondary" className="mb-4">
            Admin
          </Badge>
          <h1 className="font-heading text-3xl font-semibold tracking-normal sm:text-4xl">
            News admin
          </h1>
          <p className="mt-3 max-w-2xl text-base leading-7 text-muted-foreground">
            Review story status, authors, categories, and links from a responsive editorial dashboard.
          </p>
        </div>
        <Link href="/news" className="inline-flex items-center gap-1 text-sm font-medium text-primary">
          View public news
          <ArrowUpRight className="size-3.5" />
        </Link>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="size-4" />
              Stories
            </CardTitle>
          </CardHeader>
          <CardContent className="text-3xl font-semibold">{newsItems.length}</CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="size-4" />
              Published
            </CardTitle>
          </CardHeader>
          <CardContent className="text-3xl font-semibold">{publishedCount}</CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Editorial queue</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Title</TableHead>
                <TableHead>Category</TableHead>
                <TableHead>Author</TableHead>
                <TableHead className="text-right">Date</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {newsItems.map((item) => (
                <TableRow key={item.id}>
                  <TableCell className="min-w-64 font-medium">
                    <Link href={`/news/${item.id}`} className="hover:text-primary">
                      {item.title}
                    </Link>
                  </TableCell>
                  <TableCell>{item.category}</TableCell>
                  <TableCell>{item.author}</TableCell>
                  <TableCell className="text-right">{item.date}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
