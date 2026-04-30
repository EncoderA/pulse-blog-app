import {
  BrainCircuit,
  CalendarDays,
  ClipboardList,
  FileText,
  Flag,
  Lightbulb,
  Network,
  Rocket,
  Sparkles,
  Target,
  type LucideIcon,
} from "lucide-react";

// ─── Types ────────────────────────────────────────────────────────────────────

export type QuickTakeItem = {
  title: string;
  description: string;
  icon: LucideIcon;
};

export type ArticleSection = {
  title: string;
  body?: string;
  points?: string[];
};

export type KeyFact = {
  label: string;
  value: string;
  icon: LucideIcon;
};

export type TopQuote = {
  text: string;
  author: string;
  designation: string;
};

export type RelatedTopic = {
  name: string;
  count: number;
};

export type RelatedArticle = {
  title: string;
  date: string;
  thumbnail: string;
  icon: LucideIcon;
};

// ─── Data ─────────────────────────────────────────────────────────────────────

export const quickTake: QuickTakeItem[] = [
  {
    title: "What Happened?",
    description:
      "India announced a national AI policy focused on public infrastructure, research, governance, and sector-level adoption.",
    icon: Sparkles,
  },
  {
    title: "Why It Matters?",
    description:
      "The policy gives startups, universities, and enterprises a shared roadmap for building responsible AI at national scale.",
    icon: Lightbulb,
  },
  {
    title: "What's Next?",
    description:
      "Implementation groups will define standards, funding paths, safety guardrails, and pilot programs across priority sectors.",
    icon: Rocket,
  },
];

export const articleSections: ArticleSection[] = [
  {
    title: "Background",
    body: "India has been expanding its digital public infrastructure while domestic AI startups, research labs, and enterprise teams move from experimentation to production systems. The new policy is intended to connect these efforts under a national framework.",
  },
  {
    title: "What Happened?",
    body: "The government introduced a national AI policy outlining investment priorities, safety expectations, data access principles, and support for AI-led public services. It positions AI as a strategic technology for economic growth and administrative modernization.",
  },
  {
    title: "Key Highlights",
    points: [
      "A national AI compute and data infrastructure program for researchers, startups, and public sector teams.",
      "Responsible AI guidelines covering transparency, accountability, privacy, and human oversight.",
      "Priority pilots in healthcare, agriculture, education, public services, and language technology.",
      "Funding support for deep-tech startups, academic labs, and industry partnerships.",
    ],
  },
  {
    title: "Impact",
    body: "The policy could accelerate domestic AI development by reducing infrastructure barriers and creating clearer expectations for deployment. For businesses, the announcement signals stronger government demand for AI systems that are reliable, explainable, and locally relevant.",
  },
  {
    title: "What's Next?",
    body: "Ministries and implementation partners are expected to translate the policy into sector-specific programs, procurement standards, and safety review processes. Early progress will likely be measured through pilot outcomes, startup participation, and public infrastructure usage.",
  },
];

export const keyFacts: KeyFact[] = [
  {
    label: "Policy Announced",
    value: "May 16, 2024, with a focus on coordinated national AI adoption.",
    icon: CalendarDays,
  },
  {
    label: "Focus Areas",
    value: "Compute access, research, safety, language AI, and public services.",
    icon: Target,
  },
  {
    label: "Vision",
    value: "Build trusted AI systems that support innovation and inclusion.",
    icon: Flag,
  },
  {
    label: "Implementation",
    value: "Sector pilots, governance standards, and public-private programs.",
    icon: ClipboardList,
  },
];

export const topQuotes: TopQuote[] = [
  {
    text: "The next wave of digital growth will come from AI that solves local problems at national scale.",
    author: "Rajeev Chandrasekhar",
    designation: "Technology Policy Leader",
  },
  {
    text: "India's AI opportunity depends on trust, access, and strong research capacity.",
    author: "Nandan Nilekani",
    designation: "Digital Infrastructure Advocate",
  },
];

export const relatedTopics: RelatedTopic[] = [
  { name: "Artificial Intelligence", count: 128 },
  { name: "Digital India", count: 84 },
  { name: "Startups", count: 76 },
  { name: "Public Policy", count: 62 },
  { name: "Deep Tech", count: 41 },
];

export const relatedArticles: RelatedArticle[] = [
  {
    title: "How AI compute access could reshape India's startup ecosystem",
    date: "May 12, 2024",
    thumbnail: "bg-primary text-primary-foreground",
    icon: BrainCircuit,
  },
  {
    title: "Digital public infrastructure enters its next phase",
    date: "May 10, 2024",
    thumbnail: "bg-secondary text-secondary-foreground",
    icon: Network,
  },
  {
    title: "New governance standards emerge for high-impact AI systems",
    date: "May 08, 2024",
    thumbnail: "bg-accent text-accent-foreground",
    icon: FileText,
  },
];
