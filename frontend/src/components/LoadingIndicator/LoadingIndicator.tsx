/**
 * LoadingIndicator Component
 * 
 * Displays loading state indicators for various contexts.
 */

import React from 'react';
import { LoadingIndicatorProps } from '../../types';
import './LoadingIndicator.css';

const LoadingIndicator: React.FC<LoadingIndicatorProps> = ({
  size = 'medium',
  text,
}) => {
  const sizeClass = `loading-indicator--${size}`;
  const dotSize = size === 'small' ? '6px' : size === 'large' ? '10px' : '8px';

  return (
    <div className={`loading-indicator ${sizeClass}`} role="status" aria-live="polite">
      <div className="loading-indicator__dots">
        <span
          className="loading-indicator__dot"
          style={{ width: dotSize, height: dotSize }}
          aria-hidden="true"
        />
        <span
          className="loading-indicator__dot"
          style={{ width: dotSize, height: dotSize }}
          aria-hidden="true"
        />
        <span
          className="loading-indicator__dot"
          style={{ width: dotSize, height: dotSize }}
          aria-hidden="true"
        />
      </div>
      {text && (
        <span className="loading-indicator__text" aria-live="polite">
          {text}
        </span>
      )}
      <span className="sr-only">Loading...</span>
    </div>
  );
};

export default LoadingIndicator;

