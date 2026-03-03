import Link from "next/link";
import { Icon } from "@iconify/react";

export function Footer() {
    return (
        <footer className="w-full bg-slate-900 text-white z-50 relative">
            <div className="max-w-6xl mx-auto px-4 py-12">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
                    {/* Brand Column */}
                    <div className="col-span-1 md:col-span-2">
                        <h3 className="text-2xl font-bold mb-4 text-green-400">Cite Me</h3>
                        <p className="text-gray-400 mb-4 max-w-md">
                            Your trustworthy guide to ensure every fact you find is backed by reliable sources.
                            Fighting misinformation with credible, verified information.
                        </p>
                        <div className="flex gap-4">
                            <a
                                href="https://twitter.com"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-gray-400 hover:text-green-400 transition"
                                aria-label="Twitter"
                            >
                                <Icon icon="mdi:twitter" width="24" height="24" />
                            </a>
                            <a
                                href="https://github.com"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-gray-400 hover:text-green-400 transition"
                                aria-label="GitHub"
                            >
                                <Icon icon="mdi:github" width="24" height="24" />
                            </a>
                            <a
                                href="https://linkedin.com"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-gray-400 hover:text-green-400 transition"
                                aria-label="LinkedIn"
                            >
                                <Icon icon="mdi:linkedin" width="24" height="24" />
                            </a>
                            <a
                                href="mailto:contact@citeme.com"
                                className="text-gray-400 hover:text-green-400 transition"
                                aria-label="Email"
                            >
                                <Icon icon="mdi:email" width="24" height="24" />
                            </a>
                        </div>
                    </div>

                    {/* Product Links */}
                    <div>
                        <h4 className="text-lg font-semibold mb-4">Product</h4>
                        <ul className="space-y-2">
                            <li>
                                <Link href="#top" className="text-gray-400 hover:text-green-400 transition">
                                    Home
                                </Link>
                            </li>
                            <li>
                                <Link href="/features" className="text-gray-400 hover:text-green-400 transition">
                                    Features
                                </Link>
                            </li>
                            <li>
                                <Link href="/pricing" className="text-gray-400 hover:text-green-400 transition">
                                    Pricing
                                </Link>
                            </li>
                            <li>
                                <Link href="/api" className="text-gray-400 hover:text-green-400 transition">
                                    API
                                </Link>
                            </li>
                        </ul>
                    </div>

                    {/* Resources */}
                    <div>
                        <h4 className="text-lg font-semibold mb-4">Resources</h4>
                        <ul className="space-y-2">
                            <li>
                                <Link href="/about" className="text-gray-400 hover:text-green-400 transition">
                                    About Us
                                </Link>
                            </li>
                            <li>
                                <Link href="/blog" className="text-gray-400 hover:text-green-400 transition">
                                    Blog
                                </Link>
                            </li>
                            <li>
                                <Link href="/help" className="text-gray-400 hover:text-green-400 transition">
                                    Help Center
                                </Link>
                            </li>
                            <li>
                                <Link href="/contact" className="text-gray-400 hover:text-green-400 transition">
                                    Contact
                                </Link>
                            </li>
                        </ul>
                    </div>
                </div>

                {/* Bottom Bar */}
                <div className="border-t border-gray-800 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
                    <p className="text-gray-400 text-sm">
                        © 2025 Cite Me. All rights reserved.
                    </p>
                    <div className="flex gap-6 text-sm">
                        <Link href="/privacy" className="text-gray-400 hover:text-green-400 transition">
                            Privacy Policy
                        </Link>
                        <Link href="/terms" className="text-gray-400 hover:text-green-400 transition">
                            Terms of Service
                        </Link>
                        <Link href="/cookies" className="text-gray-400 hover:text-green-400 transition">
                            Cookie Policy
                        </Link>
                    </div>
                </div>
            </div>
        </footer>
    );
}
