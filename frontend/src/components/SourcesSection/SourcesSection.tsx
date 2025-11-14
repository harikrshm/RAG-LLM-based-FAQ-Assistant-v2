/**
 * SourcesSection Component
 * 
 * Displays source citations at the end of assistant messages.
 */

import React, { useState } from 'react';
import { SourcesSectionProps, Source } from '../../types';
import { isGrowwUrl, getDomainName } from '../../utils/linkParser';
import './SourcesSection.css';

const SourcesSection: React.FC<SourcesSectionProps> = ({ 
  sources, 
  onSourceClick 
}) => {
  const [isExpanded, setIsExpanded] = useState(true);

  if (!sources || sources.length === 0) {
    return null;
  }

  // Sort sources: Groww pages first, then by relevance score
  const sortedSources = [...sources].sort((a, b) => {
    const aIsGroww = isGrowwUrl(a.url);
    const bIsGroww = isGrowwUrl(b.url);
    
    // Groww pages first
    if (aIsGroww && !bIsGroww) return -1;
    if (!aIsGroww && bIsGroww) return 1;
    
    // Then by relevance score (higher first)
    const aScore = a.relevanceScore || 0;
    const bScore = b.relevanceScore || 0;
    return bScore - aScore;
  });

  const growwSources = sortedSources.filter(s => isGrowwUrl(s.url));
  const externalSources = sortedSources.filter(s => !isGrowwUrl(s.url));

  const handleSourceClick = (source: Source) => {
    if (onSourceClick) {
      onSourceClick(source);
    }
    // Open in new tab
    window.open(source.url, '_blank', 'noopener,noreferrer');
  };

  const renderSource = (source: Source, index: number) => {
    const isGroww = isGrowwUrl(source.url);
    const domain = getDomainName(source.url);
    
    return (
      <div
        key={index}
        className={`source-item ${isGroww ? 'source-item--groww' : ''}`}
        onClick={() => handleSourceClick(source)}
        role="button"
        tabIndex={0}
        aria-label={`Source: ${source.title || domain}`}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            handleSourceClick(source);
          }
        }}
      >
        <div className="source-item__icon">
          {isGroww ? (
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
              <polyline points="15 3 21 3 21 9" />
              <line x1="10" y1="14" x2="21" y2="3" />
            </svg>
          ) : (
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
              <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
            </svg>
          )}
        </div>
        
        <div className="source-item__content">
          <div className="source-item__header">
            <h4 className="source-item__title">
              {source.title || domain}
            </h4>
            {source.relevanceScore !== undefined && (
              <span className="source-item__score">
                {Math.round(source.relevanceScore * 100)}%
              </span>
            )}
          </div>
          
          {source.excerpt && (
            <p className="source-item__excerpt">
              {source.excerpt}
            </p>
          )}
          
          <div className="source-item__meta">
            <span className="source-item__domain">{domain}</span>
            {source.amcName && (
              <>
                <span className="source-item__separator">•</span>
                <span className="source-item__amc">{source.amcName}</span>
              </>
            )}
            {source.sourceType && source.sourceType !== 'unknown' && (
              <>
                <span className="source-item__separator">•</span>
                <span className={`source-item__type source-item__type--${source.sourceType}`}>
                  {source.sourceType === 'groww_page' && 'Groww'}
                  {source.sourceType === 'sebi_website' && 'SEBI'}
                  {source.sourceType === 'amfi_website' && 'AMFI'}
                  {source.sourceType === 'amc_website' && 'AMC'}
                </span>
              </>
            )}
          </div>
        </div>
        
        <div className="source-item__arrow">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="9 18 15 12 9 6" />
          </svg>
        </div>
      </div>
    );
  };

  return (
    <div className="sources-section">
      <button
        className="sources-section__header"
        onClick={() => setIsExpanded(!isExpanded)}
        aria-expanded={isExpanded}
        aria-label={`${isExpanded ? 'Collapse' : 'Expand'} sources`}
      >
        <div className="sources-section__header-content">
          <svg 
            className="sources-section__icon" 
            viewBox="0 0 24 24" 
            fill="none" 
            stroke="currentColor" 
            strokeWidth="2"
          >
            <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
            <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
          </svg>
          <span className="sources-section__title">
            Sources ({sources.length})
          </span>
          {growwSources.length > 0 && (
            <span className="sources-section__badge">
              {growwSources.length} Groww
            </span>
          )}
        </div>
        <svg
          className={`sources-section__chevron ${isExpanded ? 'sources-section__chevron--expanded' : ''}`}
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
        >
          <polyline points="6 9 12 15 18 9" />
        </svg>
      </button>

      {isExpanded && (
        <div className="sources-section__content">
          {growwSources.length > 0 && (
            <div className="sources-section__group">
              <h5 className="sources-section__group-title">Groww Pages</h5>
              <div className="sources-section__list">
                {growwSources.map((source, index) => renderSource(source, index))}
              </div>
            </div>
          )}

          {externalSources.length > 0 && (
            <div className="sources-section__group">
              <h5 className="sources-section__group-title">External Sources</h5>
              <div className="sources-section__list">
                {externalSources.map((source, index) => renderSource(source, growwSources.length + index))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default SourcesSection;

