"use client";

import { RetroGrid } from "@/components/ui/retro-grid";
import { Textarea } from "@/components/ui/textarea";
import { Icon } from "@iconify/react";
import { GradedText } from "@/components/ui/graded-text";
import Link from "next/link";
import Image from "next/image";
import { cn } from "@/lib/utils";
import { Marquee } from "@/components/ui/marquee";
import { OrbitingCircles } from "@/components/ui/orbiting-circles";
import { useRouter } from "next/navigation";
import { useState } from "react";

const reviews = [
    {
        name: "Dr. Sarah Mitchell",
        username: "@drsarahmitchell",
        body: "Cite Me transformed my research workflow. The credibility scores help me quickly identify which sources need more investigation before citing them in my papers.",
        img: "https://avatar.vercel.sh/sarah",
    },
    {
        name: "Alex Rivera",
        username: "@alexnewsdesk",
        body: "As a journalist, fact-checking is crucial. This tool catches questionable claims I might have missed and provides clear evidence ratings for each assertion.",
        img: "https://avatar.vercel.sh/alex",
    },
    {
        name: "Emily Chen",
        username: "@emilychen_student",
        body: "Finally aced my essay! The detailed breakdown showing which parts of my argument were well-supported helped me strengthen my thesis significantly.",
        img: "https://avatar.vercel.sh/emily",
    },
    {
        name: "Prof. James Carter",
        username: "@profcarter_edu",
        body: "I recommend Cite Me to all my students. It teaches them to critically evaluate sources and understand the difference between opinion and verified fact.",
        img: "https://avatar.vercel.sh/james",
    },
    {
        name: "Maria Lopez",
        username: "@maria_factcheck",
        body: "The transparency is what sold me. For each claim, I can see exactly which sources support or contradict it, with clear explanations of the methodology.",
        img: "https://avatar.vercel.sh/maria",
    },
    {
        name: "David Wong",
        username: "@davidwong_writer",
        body: "My editor loves that I can now provide credibility scores alongside my articles. It adds an extra layer of trust and professionalism to my work.",
        img: "https://avatar.vercel.sh/david",
    },
]

const firstRow = reviews.slice(0, reviews.length / 2)
const secondRow = reviews.slice(reviews.length / 2)

const ReviewCard = ({
    img,
    name,
    username,
    body,
}: {
    img: string
    name: string
    username: string
    body: string
}) => {
    return (
        <figure
            className={cn(
                "relative h-full w-64 cursor-pointer overflow-hidden rounded-xl border p-4",
                // light styles
                "border-gray-950/10 bg-gray-950/1 hover:bg-gray-950/5",
                // dark styles
                "dark:border-gray-50/10 dark:bg-gray-50/10 dark:hover:bg-gray-50/15"
            )}
        >
            <div className="flex flex-row items-center gap-2">
                <img className="rounded-full" width={32} height={32} alt="" src={img} />
                <div className="flex flex-col">
                    <figcaption className="text-sm font-medium dark:text-white">
                        {name}
                    </figcaption>
                    <p className="text-xs font-medium dark:text-white/40">{username}</p>
                </div>
            </div>
            <blockquote className="mt-2 text-sm">{body}</blockquote>
        </figure>
    )
}
export default function Home() {
    const router = useRouter();
    const [text, setText] = useState("");

    const handleSubmit = () => {
        if (!text.trim()) {
            alert("Please enter some text to analyze.");
            return;
        }
        
        // Generate a unique ID for this analysis
        const rid = `${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
        
        // Store the text in sessionStorage
        sessionStorage.setItem(`text-${rid}`, text);
        
        // Navigate to result page
        router.push(`/result/${rid}`);
    };

    return (
        <>
            {/* Hero Section */}
            <div id="top" className="relative h-[700px] w-full overflow-hidden">
                <RetroGrid className='absolute h-[750px]' />
                <div className="h-full flex items-center justify-center w-full">
                    <div className="text-center max-w-[800px] relative pb-[100px] m-5">
                        <GradedText grade={100} className="text-6xl font-extrabold">
                            Cite Me
                        </GradedText>
                        <div className="text-lg my-5">
                            Verify claims and check facts instantly. Analyze any text to assess the credibility of its assertions with AI-powered source verification.
                        </div>

                        <div className="my-5 absolute w-full h-auto transition-all">
                            <Textarea
                                value={text}
                                onChange={(e) => setText(e.target.value)}
                                placeholder="Paste any text, article, or claim to verify its accuracy and get credibility scores..."
                                className="overflow-y-auto placeholder:text-gray-500 transition-all min-h-20 max-h-[200px] h-auto w-full border-0 bg-gray-400/20 backdrop-blur-xs p-2 pl-4 resize-none focus:min-h-[200px] rounded-[20px]"
                            />

                            <button
                                onClick={handleSubmit}
                                onMouseDown={(e) => e.preventDefault()}
                                aria-label="Submit text for analysis"
                                className="absolute bottom-0 right-0 m-1 rounded-full bg-green-400 h-10 w-10 flex items-center justify-center cursor-pointer hover:bg-green-500 transition text-white hover:rotate-360"
                            >
                                <Icon icon="lucide:check" width="24" height="24" />
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            {/* Section 1: Verify Claims Instantly */}
            <section className="w-full bg-green-400 py-16 h-[800px] flex items-center justify-center">
                <div className="max-w-5xl mx-auto px-4 flex flex-col md:flex-row items-center gap-10">
                    <div className="w-full md:w-1/2 flex justify-center">
                        <Image
                            src="/images/section1.png"
                            alt="Fact checking illustration"
                            width={500}
                            height={350}
                            className="rounded-2xl shadow-lg object-cover"
                        />
                    </div>
                    <div className="w-full md:w-1/2 text-white">
                        <h2 className="text-3xl font-bold mb-4">
                            AI-Powered Fact Verification
                        </h2>
                        <p className="mb-6 leading-relaxed">
                            Paste any text or claim you want to verify. Our advanced AI system automatically analyzes each statement, identifies key assertions, and cross-references them against trusted, authoritative sources to determine their accuracy.
                        </p>
                        <Link
                            href="#top"
                            className="inline-flex items-center px-6 py-2 rounded-full bg-white text-green-600 font-semibold hover:bg-gray-100 transition"
                        >
                            Try Now
                        </Link>
                    </div>
                </div>
            </section>

            {/* Section 2: Credibility Scoring */}
            <section className="w-full bg-white py-16 h-[800px] flex items-center justify-center">
                <div className="max-w-5xl mx-auto px-4 flex flex-col md:flex-row-reverse items-center gap-10">
                    <div className="w-full md:w-1/2 flex justify-center">
                        <Image
                            src="/images/section2.png"
                            alt="Citation and sources"
                            width={500}
                            height={350}
                            className="rounded-2xl shadow-lg object-cover"
                        />
                    </div>
                    <div className="w-full md:w-1/2 text-gray-900">
                        <h2 className="text-3xl font-bold mb-4">
                            Detailed Credibility Reports
                        </h2>
                        <p className="mb-6 leading-relaxed">
                            Receive comprehensive analysis with credibility scores for every assertion. Each claim is graded from 0 to 100 based on supporting evidence, source reliability, and factual accuracy. Understand exactly why each statement receives its score with transparent explanations.
                        </p>
                        <Link
                            href="#top"
                            className="inline-flex items-center px-6 py-2 rounded-full bg-green-500 text-white font-semibold hover:bg-green-600 transition"
                        >
                            Try Now
                        </Link>
                    </div>
                </div>
            </section>

            {/* Section 3: Make Informed Decisions */}
            <section className="w-full bg-green-400 py-16 h-[800px] flex items-center justify-center">
                <div className="max-w-5xl mx-auto px-4 flex flex-col md:flex-row items-center gap-10">
                    <div className="w-full md:w-1/2 flex justify-center">
                        <div className="relative flex h-[500px] w-[500px] items-center justify-center">
                            <div className="text-2xl text-white font-bold">Cite Me</div>
                            <OrbitingCircles iconSize={70} radius={90} duration={10}>
                                <div className="h-15 w-15 rounded-full bg-white overflow-hidden outline-white outline-2">
                                    <img src="/images/section3-1.png" alt="" className="" />
                                </div>
                                <div className="h-15 w-15 rounded-full bg-white overflow-hidden outline-white outline-2">
                                    <img src="/images/section3-2.png" alt="" className="" />
                                </div>
                                <div className="h-15 w-15 rounded-full bg-white overflow-hidden outline-white outline-2">
                                    <img src="/images/section3-3.png" alt="" className="" />
                                </div>
                                <div className="h-15 w-15 rounded-full bg-white overflow-hidden outline-white outline-2">
                                    <img src="/images/section3-4.png" alt="" className="" />
                                </div>
                            </OrbitingCircles>
                            <OrbitingCircles iconSize={70} radius={170} duration={20} reverse={true}>
                                <div className="h-15 w-15 rounded-full bg-white overflow-hidden outline-white outline-2">
                                    <img src="/images/section3-3.png" alt="" className="" />
                                </div>
                                <div className="h-15 w-15 rounded-full bg-white overflow-hidden outline-white outline-2">
                                    <img src="/images/section3-4.png" alt="" className="" />
                                </div>
                            </OrbitingCircles>
                        </div>
                    </div>
                    <div className="w-full md:w-1/2 text-white">
                        <h2 className="text-3xl font-bold mb-4">
                            Academic & Professional Ready
                        </h2>
                        <p className="mb-6 leading-relaxed">
                            Perfect for students, researchers, journalists, and professionals. Get properly formatted citations for each verified source. Use our detailed reports to strengthen your academic papers, news articles, or business documents with credible, well-sourced information.
                        </p>
                        <Link
                            href="#top"
                            className="inline-flex items-center px-6 py-2 rounded-full bg-white text-green-600 font-semibold hover:bg-gray-100 transition"
                        >
                            Try Now
                        </Link>
                    </div>
                </div>
            </section>

            {/* User Testimonials */}
            <section className="w-full bg-white py-16 h-[800px] flex items-center justify-center">
                <div className="max-w-5xl mx-auto px-4 flex flex-col md:flex-row-reverse items-center gap-10">
                    <div className="w-full h-full relative">

                        <h2 className="text-3xl font-bold mb-4 text-center text-gray-900">
                            Trusted by Researchers, Students & Journalists
                        </h2>
                        <div className="relative flex w-full flex-col items-center justify-center overflow-hidden ">

                            <Marquee pauseOnHover className="[--duration:20s] my-2">
                                {firstRow.map((review) => (
                                    <ReviewCard key={review.username} {...review} />
                                ))}
                            </Marquee>
                            <Marquee reverse pauseOnHover className="[--duration:20s]">
                                {secondRow.map((review) => (
                                    <ReviewCard key={review.username} {...review} />
                                ))}
                            </Marquee>
                            <div className="from-background pointer-events-none absolute inset-y-0 left-0 w-1/4 bg-linear-to-r [--background:white]"></div>
                            <div className="from-background pointer-events-none absolute inset-y-0 right-0 w-1/4 bg-linear-to-l [--background:white]"></div>

                            <Link
                                href="#top"
                                className="inline-flex items-center px-6 py-2 rounded-full bg-green-500 text-white font-semibold hover:bg-green-600 transition my-6"
                            >
                                Try Now
                            </Link>
                        </div>
                    </div>
                </div>
            </section>
        </>
    );
}