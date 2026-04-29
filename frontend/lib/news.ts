export type NewsItem = {
  id: string
  title: string
  excerpt: string
  body: string[]
  timeline: {
    date: string
    title: string
    description: string
  }[]
  category: string
  author: string
  date: string
  readTime: string
  status: "Published" | "Draft" | "Review"
}

export const newsItems: NewsItem[] = [
  {
    id: "global-markets-open-mixed",
    title: "Global markets open mixed as investors watch earnings",
    excerpt:
      "Major indexes moved in different directions as traders weighed company results, energy prices, and policy signals.",
    body: [
      "Global markets opened mixed as investors assessed a fresh round of earnings reports and shifting expectations for interest-rate policy.",
      "Technology shares showed early strength, while energy and transport names traded unevenly after another volatile session for oil prices.",
      "Analysts said the next set of inflation and jobs data could shape sentiment through the rest of the week.",
    ],
    timeline: [
      {
        date: "Apr 26, 2026",
        title: "Oil prices swing before the open",
        description:
          "Energy traders reacted to supply concerns, putting pressure on transport and industrial shares.",
      },
      {
        date: "Apr 27, 2026",
        title: "Earnings reports split sentiment",
        description:
          "Large-cap results gave investors mixed signals across technology, consumer, and financial names.",
      },
      {
        date: "Apr 28, 2026",
        title: "Indexes open in different directions",
        description:
          "Technology shares gained early while energy and transport stocks traded unevenly.",
      },
    ],
    category: "Business",
    author: "Maya Shah",
    date: "Apr 28, 2026",
    readTime: "4 min read",
    status: "Published",
  },
  {
    id: "parliament-debates-digital-bill",
    title: "Parliament debates new digital services bill",
    excerpt:
      "Lawmakers are reviewing rules covering platform accountability, consumer data rights, and online transparency.",
    body: [
      "Parliament opened debate on a digital services bill that would set new obligations for large online platforms.",
      "The proposal includes consumer data protections, stronger complaint handling requirements, and transparency reports for major service providers.",
      "Supporters argue the bill modernizes oversight, while critics want narrower language around enforcement and compliance costs.",
    ],
    timeline: [
      {
        date: "Apr 24, 2026",
        title: "Draft bill enters the chamber",
        description:
          "Lawmakers received the digital services proposal for initial review and committee scheduling.",
      },
      {
        date: "Apr 26, 2026",
        title: "Consumer data rules draw focus",
        description:
          "Members highlighted platform accountability, complaint handling, and data rights as core points.",
      },
      {
        date: "Apr 27, 2026",
        title: "Debate opens on enforcement scope",
        description:
          "Supporters defended modernization goals while critics questioned compliance costs and broad language.",
      },
    ],
    category: "Policy",
    author: "Daniel Lee",
    date: "Apr 27, 2026",
    readTime: "3 min read",
    status: "Review",
  },
  {
    id: "studio-announces-summer-film-slate",
    title: "Studio announces expanded summer film slate",
    excerpt:
      "The release calendar adds two original dramas, a family animation title, and a late-season thriller.",
    body: [
      "A major studio announced an expanded summer film slate, adding four titles to a calendar already crowded with franchise releases.",
      "Executives said the mix of original drama, animation, and suspense programming is meant to reach audiences across theaters and streaming windows.",
      "Industry watchers will be tracking opening weekends closely after a cautious start to the season.",
    ],
    timeline: [
      {
        date: "Apr 21, 2026",
        title: "Release calendar review begins",
        description:
          "Studio executives evaluated gaps in the summer schedule after a cautious start to the season.",
      },
      {
        date: "Apr 23, 2026",
        title: "Four titles added to the slate",
        description:
          "The studio placed two dramas, one family animation title, and a thriller into the calendar.",
      },
      {
        date: "Apr 25, 2026",
        title: "Expanded slate is announced",
        description:
          "Industry watchers began tracking how the new mix could affect theatrical and streaming windows.",
      },
    ],
    category: "Entertainment",
    author: "Avery Chen",
    date: "Apr 25, 2026",
    readTime: "5 min read",
    status: "Published",
  },
  {
    id: "city-opens-new-transit-corridor",
    title: "City opens new transit corridor after two-year build",
    excerpt:
      "The route adds faster cross-town service, redesigned bus stops, and new protected cycling connections.",
    body: [
      "The city opened a new transit corridor designed to shorten cross-town travel times and reduce pressure on crowded routes.",
      "The project includes redesigned bus stops, signal priority at key intersections, and protected cycling connections along the main avenue.",
      "Officials said ridership and traffic data will be reviewed over the first quarter before service frequency is adjusted.",
    ],
    timeline: [
      {
        date: "Apr 20, 2024",
        title: "Corridor construction begins",
        description:
          "Crews started the two-year build for bus priority lanes, redesigned stops, and cycling connections.",
      },
      {
        date: "Mar 18, 2026",
        title: "Signal priority testing starts",
        description:
          "Transport teams tested intersection timing and stop placement before public service began.",
      },
      {
        date: "Apr 23, 2026",
        title: "Transit corridor opens",
        description:
          "The city launched the route and began collecting ridership and traffic data for review.",
      },
    ],
    category: "Community",
    author: "Priya Raman",
    date: "Apr 23, 2026",
    readTime: "4 min read",
    status: "Draft",
  },
]

export function getNewsItem(id: string) {
  return newsItems.find((item) => item.id === id)
}
