"use client"
import "./globals.css";
import * as React from "react"
import {NavigationMenuDemo} from "@/components/ui/nav";
import {Footer} from "@/components/ui/footer";

export default function Home({
    children,
}: {
    children: React.ReactNode
}) {
    return (
    <html className="scroll-smooth">
        <body>
            <NavigationMenuDemo/>
            <div>
                {children}
            </div>
            <Footer/>
        </body>
    </html>
    )
}

