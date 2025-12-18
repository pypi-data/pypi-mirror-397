/**
 * Collapsible Section Component
 *
 * A collapsible section with header, badge, and content.
 */

import React, { useState, ReactNode } from 'react';

interface SectionProps {
    id: string;
    title: string;
    badge: string;
    badgeIcon: string;
    variant: 'incoming' | 'transform' | 'outgoing' | 'json';
    description?: string;
    defaultCollapsed?: boolean;
    headerExtra?: ReactNode;
    children: ReactNode;
}

export function Section({
    id,
    title,
    badge,
    badgeIcon,
    variant,
    description,
    defaultCollapsed = false,
    headerExtra,
    children,
}: SectionProps) {
    const [isCollapsed, setIsCollapsed] = useState(defaultCollapsed);

    return (
        <div className={`section section--${variant}`}>
            <div
                className="section__header"
                onClick={() => setIsCollapsed(!isCollapsed)}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                        setIsCollapsed(!isCollapsed);
                    }
                }}
            >
                <span className={`section__chevron ${isCollapsed ? 'section__chevron--collapsed' : ''}`}>
                    ▼
                </span>
                <span className={`section__badge section__badge--${variant}`}>
                    {badgeIcon} {badge}
                </span>
                <h2 className="section__title">{title}</h2>
                {headerExtra}
            </div>
            <div className={`section__content ${isCollapsed ? 'section__content--collapsed' : ''}`}>
                {description && <p className="section__description">{description}</p>}
                {children}
            </div>
        </div>
    );
}
