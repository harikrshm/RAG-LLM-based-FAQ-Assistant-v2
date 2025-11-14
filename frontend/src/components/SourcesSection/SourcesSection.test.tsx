/**
 * Unit tests for SourcesSection component
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { SourcesSection } from './SourcesSection';
import { Source } from '../../types/components';

describe('SourcesSection', () => {
  const mockSources: Source[] = [
    {
      url: 'https://groww.in/fund1',
      title: 'Fund 1',
      sourceType: 'groww_page',
      amcName: 'Test AMC',
      relevanceScore: 0.95,
    },
    {
      url: 'https://example.com/fund2',
      title: 'Fund 2',
      sourceType: 'amc_website',
      relevanceScore: 0.85,
    },
  ];

  it('renders sources section with title', () => {
    render(<SourcesSection sources={mockSources} />);
    
    expect(screen.getByText('Sources:')).toBeInTheDocument();
  });

  it('renders all sources', () => {
    render(<SourcesSection sources={mockSources} />);
    
    expect(screen.getByText('Fund 1')).toBeInTheDocument();
    expect(screen.getByText('Fund 2')).toBeInTheDocument();
  });

  it('renders source items correctly', () => {
    render(<SourcesSection sources={mockSources} />);
    
    expect(screen.getByText('Fund 1')).toBeInTheDocument();
    expect(screen.getByText('Fund 2')).toBeInTheDocument();
  });

  it('does not render when sources array is empty', () => {
    const { container } = render(<SourcesSection sources={[]} />);
    
    expect(container.firstChild).toBeNull();
  });

  it('displays AMC name when available', () => {
    render(<SourcesSection sources={mockSources} />);
    
    expect(screen.getByText(/Test AMC/i)).toBeInTheDocument();
  });

  it('handles sources without titles', () => {
    const sourcesWithoutTitles: Source[] = [
      {
        url: 'https://example.com',
        sourceType: 'groww_page',
      },
    ];

    render(<SourcesSection sources={sourcesWithoutTitles} />);
    
    expect(screen.getByText(/example.com/i)).toBeInTheDocument();
  });

  it('sorts sources with Groww pages first', () => {
    render(<SourcesSection sources={mockSources} />);
    
    const sourceItems = screen.getAllByText(/Fund/i);
    // Groww source should appear first
    expect(sourceItems[0]).toHaveTextContent('Fund 1');
  });
});

