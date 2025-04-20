"use client";

import type React from "react";

import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import Link from "next/link"

import { Trophy, ArrowUpDown, BarChart2 } from "lucide-react";

// Define the type for our leaderboard entries
type LeaderboardEntry = {
  id: string;
  similarityPercentage: number;
  name: string;
  hackathonName: string;
  date: string;
  location: string;
};

// Sample data for the leaderboard
const initialLeaderboardData: LeaderboardEntry[] = [
  {
    id: "1",
    similarityPercentage: 92,
    name: "Alex Johnson",
    hackathonName: "TechCrunch Disrupt",
    date: "2023-09-15",
    location: "San Francisco, CA",
  },
  {
    id: "2",
    similarityPercentage: 87,
    name: "Maria Garcia",
    hackathonName: "HackMIT",
    date: "2023-10-02",
    location: "Cambridge, MA",
  },
  {
    id: "3",
    similarityPercentage: 25,
    name: "James Wilson",
    hackathonName: "PennApps",
    date: "2023-08-25",
    location: "Philadelphia, PA",
  },
  {
    id: "4",
    similarityPercentage: 50,
    name: "Sarah Kim",
    hackathonName: "HackNY",
    date: "2023-11-10",
    location: "New York, NY",
  },
  {
    id: "5",
    similarityPercentage: 10,
    name: "David Chen",
    hackathonName: "TreeHacks",
    date: "2023-07-20",
    location: "Stanford, CA",
  },
];

const ProgressBar = ({ value }: { value: number }) => {
  const getColor = (percentage: number) => {
    const hue = percentage * 1.2; // 0 to 120 (red to green)
    const saturation = 75;
    const lightness = 50;

    // Calculate perceived brightness to determine text color
    // Using relative luminance formula
    const getBrightness = (h: number, s: number, l: number) => {
      // Convert HSL to RGB first (simplified conversion)
      const c = ((1 - Math.abs((2 * l) / 100 - 1)) * s) / 100;
      const x = c * (1 - Math.abs(((h / 60) % 2) - 1));
      const m = l / 100 - c / 2;

      let r, g, b;
      if (h < 60) {
        [r, g, b] = [c, x, 0];
      } else if (h < 120) {
        [r, g, b] = [x, c, 0];
      } else {
        [r, g, b] = [0, c, 0];
      }

      // Calculate relative luminance
      return ((r + m) * 0.299 + (g + m) * 0.587 + (b + m) * 0.114) * 100;
    };

    const brightness = getBrightness(hue, saturation, lightness);
    const textColor = brightness > 50 ? "#1a1a1a" : "#ffffff";

    return {
      backgroundColor: `hsl(${hue}, ${saturation}%, ${lightness}%)`,
      color: textColor,
    };
  };

  return (
    <div className="w-full bg-gray-200 rounded-full h-6 overflow-hidden relative">
      <div
        className="h-full flex items-center justify-center text-xs font-medium absolute"
        style={{
          width: `${value}%`,
          backgroundColor: getColor(value).backgroundColor,
        }}
      />
      <div className="absolute inset-0 flex items-center justify-center text-xs font-medium">
        {value}%
      </div>
    </div>
  );
};

export default function Home() {
  const [url, setUrl] = useState("");
  const [leaderboardData, setLeaderboardData] = useState<LeaderboardEntry[]>(
    [...initialLeaderboardData].sort(
      (a, b) => b.similarityPercentage - a.similarityPercentage
    )
  );
  const [sortCount, setSortCount] = useState(1);

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Function to handle URL submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!url) {
      setError("Please enter a URL");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // In a real application, you would fetch data from an API here
      // For this example, we'll just simulate a network request
      await new Promise((resolve) => setTimeout(resolve, 1000));

      // Simulate getting new data based on the URL
      // In a real app, this would come from your backend
      const newEntry: LeaderboardEntry = {
        id: (leaderboardData.length + 1).toString(),
        similarityPercentage: Math.floor(Math.random() * 30) + 70, // Random percentage between 70-99
        name: "New Participant",
        hackathonName: "URL Hackathon",
        date: new Date().toISOString().split("T")[0],
        location: "Web, Remote",
      };

      // Add the new entry and sort by familiarity percentage
      setLeaderboardData(
        [...leaderboardData, newEntry].sort(
          (a, b) => b.similarityPercentage - a.similarityPercentage
        )
      );

      // Clear the input
      setUrl("");
    } catch (err) {
      setError("Failed to process the URL. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const sortLeaderboardBySimilarity = (factor: number) => {
    setLeaderboardData(
      [...initialLeaderboardData].sort(
        (a, b) => factor * (b.similarityPercentage - a.similarityPercentage)
      )
    );
  };

  return (
    <main className="flex min-h-screen flex-col items-center p-8">
      <div className="max-w-5xl w-full space-y-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold tracking-tight mb-2">
            Hackathon Leaderboard
          </h1>
          <Link href="/topics">
            <Button variant="outline" size="sm" className="gap-2">
              <BarChart2 className="h-4 w-4" />
              View Topics Chart
            </Button>
          </Link>
          <p className="text-muted-foreground">
            Enter a URL to add a new entry or view the current rankings
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Add New Entry</CardTitle>
            <CardDescription>
              Enter a URL to fetch and add a new leaderboard entry
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="flex gap-2">
              <Input
                type="url"
                placeholder="https://example.com"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                className="flex-1"
              />
              <Button type="submit" disabled={isLoading}>
                {isLoading ? "Processing..." : "Submit"}
              </Button>
            </form>
            {error && <p className="text-red-500 mt-2 text-sm">{error}</p>}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Trophy className="h-5 w-5 text-yellow-500" />
                Leaderboard Rankings
              </CardTitle>
              <CardDescription>Sorted by similarity percentage</CardDescription>
            </div>
          </CardHeader>
          <CardContent>
            <Table>
              <TableCaption>Current leaderboard standings</TableCaption>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[50px]">Rank</TableHead>
                  <TableHead className="w-[150px]">
                    <div className="flex items-center">
                      Similarity %
                      <ArrowUpDown
                        className="ml-2 h-4 w-4 cursor-pointer active:scale-75"
                        onClick={() => {
                          sortLeaderboardBySimilarity(sortCount);
                          setSortCount((prev) => (prev == 1 ? -1 : prev + 1));
                        }}
                      />
                    </div>
                  </TableHead>
                  <TableHead>Project Name</TableHead>
                  <TableHead>Hackathon</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead>Location</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {leaderboardData.map((entry, index) => (
                  <TableRow key={entry.id}>
                    <TableCell className="font-medium">{index + 1}</TableCell>
                    <TableCell>
                      <ProgressBar value={entry.similarityPercentage} />
                    </TableCell>
                    <TableCell>{entry.name}</TableCell>
                    <TableCell>{entry.hackathonName}</TableCell>
                    <TableCell>{entry.date}</TableCell>
                    <TableCell>{entry.location}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>
    </main>
  );
}
