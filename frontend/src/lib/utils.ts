import { clsx } from "clsx";
import { twMerge } from "tailwind-merge"

export function cn(...inputs: any[]) {
  return twMerge(clsx(inputs));
}

export function formatDateTime(date: string | Date) {
  const d = typeof date === "string" ? new Date(date) : date;
  return d.toLocaleString("en-PH", { month: "short", day: "numeric", year: "numeric", hour: "2-digit", minute: "2-digit" });
}
