"use client"
import Link from "next/link"
import { Bar, BarChart, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts"
import { ChartContainer, ChartTooltipContent } from "@/components/ui/chart"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { ArrowLeft, BarChart2 } from "lucide-react"

// Sample data for hackathon topics
const topicData = [
  { topic: "Artificial Intelligence", count: 78 },
  { topic: "Web3 / Blockchain", count: 65 },
  { topic: "Healthcare Tech", count: 52 },
  { topic: "Climate Tech", count: 48 },
  { topic: "EdTech", count: 43 },
  { topic: "Fintech", count: 39 },
  { topic: "AR/VR", count: 35 },
  { topic: "IoT", count: 32 },
  { topic: "Cybersecurity", count: 28 },
  { topic: "Social Impact", count: 25 },
]

export default function TopicsPage() {
  // Sort data by count in descending order
  const sortedData = [...topicData].sort((a, b) => b.count - a.count)

  return (
    <main className="flex min-h-screen flex-col items-center p-8">
      <div className="max-w-5xl w-full space-y-8">
        <div className="flex justify-between items-center">
          <Link href="/">
            <Button variant="outline" size="sm" className="gap-2">
              <ArrowLeft className="h-4 w-4" />
              Back to Leaderboard
            </Button>
          </Link>
        </div>

        <div className="text-center">
          <h1 className="text-4xl font-bold tracking-tight mb-2">Hackathon Topics</h1>
          <p className="text-muted-foreground">Most common topics across hackathon events</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart2 className="h-5 w-5 text-primary" />
              Popular Topics
            </CardTitle>
            <CardDescription>Distribution of topics across all hackathon events</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[500px] w-full">
              <ChartContainer
                config={{
                  topic: {
                    label: "Topic",
                  },
                  count: {
                    label: "Number of Hackathons",
                    color: "hsl(var(--chart-1))",
                  },
                }}
              >
                <BarChart
                  data={sortedData}
                  layout="vertical"
                  margin={{ top: 10, right: 30, left: 100, bottom: 10 }}
                  barSize={20}
                >
                  <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} />
                  <XAxis type="number" />
                  <YAxis dataKey="topic" type="category" tick={{ fontSize: 14 }} width={100} />
                  <Tooltip content={<ChartTooltipContent indicator="dashed" />} />
                  <Bar dataKey="count" fill="var(--color-count)" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ChartContainer>
            </div>
          </CardContent>
        </Card>
      </div>
    </main>
  )
}
