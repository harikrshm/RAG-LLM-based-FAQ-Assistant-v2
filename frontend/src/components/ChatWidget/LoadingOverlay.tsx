/**
 * LoadingOverlay Component
 * 
 * Optional overlay loading indicator for the entire chat widget.
 */

import React from 'react';
import { LoadingIndicator } from '../LoadingIndicator';
import './LoadingOverlay.css';

interface LoadingOverlayProps {
  show: boolean;
  message?: string;
}

const LoadingOverlay: React.FC<LoadingOverlayProps> = ({ 
  show, 
  message = 'Processing...' 
}) => {
  if (!show) return null;

  return (
    <div className="loading-overlay" role="status" aria-live="polite">
      <div className="loading-overlay__content">
        <LoadingIndicator size="large" text={message} />
      </div>
    </div>
  );
};

export default LoadingOverlay;

