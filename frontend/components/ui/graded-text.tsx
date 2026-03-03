"use client"
import React from "react";
import { getScoreColor, COLOR_CLASS_MAP } from "@/lib/grading-system";
import styles from "./graded-text.module.css";

/**
 * GradedText
 *
 * Usage:
 * <GradedText grade={85} className="...">Label</GradedText>
 *
 * Props:
 * - grade: number (percentage score, default 100)
 * - color: 'auto' or explicit color key (green | blue | yellow | red | black)
 * - showUnderline: boolean (default true)
 * - Any other standard div attributes (id, data-*, aria-*, onClick, style, className, etc.) are forwarded to the root element.
 *
 * Behavior:
 * - When `color` is 'auto', the numeric grade is converted to a letter (A-F) and mapped to a color using the unified grading system.
 */

export interface GradedTextProps extends React.HTMLAttributes<HTMLDivElement> {
    children?: React.ReactNode | string;
    grade?: number;
    color?: string;
    showUnderline?: boolean;
}

export function GradedText({ children, grade = 100, color = 'auto', showUnderline = true, className, ...rest }: GradedTextProps) {
    let resolvedColor = color;

    if (resolvedColor === 'auto') {
        // Use the unified grading system to determine color
        resolvedColor = getScoreColor(grade ?? 0);
    }

    // Use the unified color class mapping
    const textColorClass = COLOR_CLASS_MAP[resolvedColor] ?? 'text-black';
    const underlineClass = showUnderline ? 'underline' : '';

    return (
        <span className={`relative ${className ?? ''}`} {...rest}>
            <span className={[underlineClass, textColorClass].join(' ')}>
                {children}
            </span>
            <sup className={`font-normal no-underline text-[0.5em] ${textColorClass} ${styles.gradeSuperscript}`}>[{grade}]</sup>
        </span>
    );
}
