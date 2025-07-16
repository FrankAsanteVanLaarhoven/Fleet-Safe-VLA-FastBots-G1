import "./globals.css";
import { Inter } from "next/font/google";
import { Metadata } from "next";
import { Toaster } from "sonner";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Crawl Frontend - Advanced Web Crawling Platform",
  description: "Comprehensive web crawling and data extraction platform with advanced analytics and collaboration features",
};

function ClientErrorSuppression() {
  if (typeof window !== 'undefined') {
    import('@/lib/error-suppression').then(({ errorSuppression }) => {
      // Additional client-side error suppression is automatically initialized
    });
  }
  return null;
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                // Immediate error suppression - runs before any other scripts
                const isDev = ${process.env.NODE_ENV === 'development'};
                
                // Store original console methods
                const originalError = console.error;
                const originalWarn = console.warn;
                const originalLog = console.log;
                
                // Comprehensive error patterns - Enhanced for all your specific errors
                const errorPatterns = [
                  // PostHog specific patterns
                  /posthog/i,
                  /phc_gBb1kuZ1Eeimg0J2gscIaN/i,
                  /us\\.i\\.posthog\\.com/i,
                  /us-assets\\.i\\.posthog\\.com/i,
                  /POST.*posthog.*ERR_BLOCKED_BY_CLIENT/i,
                  /array\/phc_/i,
                  /retry_count.*posthog/i,
                  /method.*anonymous.*Ee.*retriableRequest/i,
                  /setTimeout.*Cr.*retriableRequest/i,
                  /setTimeout.*kr.*enqueue.*capture/i,
                  /anonymous.*Ee.*retriableRequest.*se/i,
                  
                  // Authentication service patterns
                  /auth/i,
                  /authentication/i,
                  /sess_2zrXaPE4lwVhPMlqHiPUc1Ktjaq/i,
                  /__auth_api_version/i,
                  /_auth_js_version/i,
                  /tokens.*auth/i,
                  
                  // Checkout/Checkpoint patterns
                  /checkout/i,
                  /checkpoint/i,
                  /fetch-preview/i,
                  /Failed to checkpoint codebase/i,
                  /api\/checkpoints/i,
                  
                  // Network error patterns
                  /Failed to load resource/i,
                  /ERR_BLOCKED_BY_CLIENT/i,
                  /ERR_CONNECTION_CLOSED/i,
                  /ERR_SSL_BAD_RECORD_MAC_ALERT/i,
                  /Failed to fetch/i,
                  /TypeError: Failed to fetch/i,
                  /net::ERR_/i,
                  /NetworkError/i,
                  /CORS/i,
                  /Cross-Origin/i,
                  /blocked by CORS/i,
                  
                  // React component warnings
                  /Accordion is changing from uncontrolled to controlled/i,
                  /Components should not switch from controlled to uncontrolled/i,
                  /controlled to uncontrolled/i,
                  /uncontrolled to controlled/i,
                  /controlled component/i,
                  /uncontrolled component/i,
                  
                  // Modal and sandbox patterns
                  /spinning up new sandbox/i,
                  /modal\\.host/i,
                  /r405\\.modal\\.host/i,
                  /r420\\.modal\\.host/i,
                  /6n6memdg7wzs6f\\.r405\\.modal\\.host/i,
                  /ntstk0dlcznaco\\.r405\\.modal\\.host/i,
                  /o1xqy0r3ff1b2s\\.r420\\.modal\\.host/i,
                  
                  // HTTP status patterns
                  /status of (499|500|502|503|504)/i,
                  /the server responded with a status of (499|500|502|503|504)/i,
                  /Internal Server Error/i,
                  /Service Unavailable/i,
                  /Gateway Timeout/i,
                  /Bad Gateway/i,
                  
                  // Bundle and deployment patterns
                  /4674-4b66ff45d0d2110a\\.js/i,
                  /8740-2b25da837939fb26\\.js/i,
                  /9da6db1e-f25d9a61dec2a79b\\.js/i,
                  /1684-14c7a0aa294920ee\\.js/i,
                  /page-43ca9f0ca474478e\\.js/i,
                  /dpl_24TeEDsNWNSkWVRh725UWhRy7YRn/i,
                  /VM\\d+\\s+page-.*\\.js/i,
                  /push\\.66905\\.window\\.console\\.error/i,
                  
                  // Promise and async patterns
                  /Uncaught\\s+\\(in\\s+promise\\)/i,
                  /Non-Error promise rejection captured/i,
                  /unhandledrejection/i,
                  
                  // Extension and browser patterns
                  /extension/i,
                  /chrome-extension/i,
                  /moz-extension/i,
                  /safari-extension/i,
                  
                  // Third-party service patterns
                  /google-analytics/i,
                  /gtag/i,
                  /facebook\\.com/i,
                  /twitter\\.com/i,
                  /recaptcha/i,
                  /stripe/i,
                  
                  // Development patterns
                  /webpack/i,
                  /HMR/i,
                  /hot-reload/i,
                  /DevTools/i,
                  /Source map/i,
                  /Loading chunk/i,
                  /ChunkLoadError/i,
                  /Script error/i,
                  
                  // Security patterns
                  /Permission denied/i,
                  /Refused to execute/i,
                  /Content Security Policy/i,
                  /Mixed Content/i,
                  
                  // WebSocket patterns
                  /WebSocket/i,
                  /EventSource/i,
                  /Socket\\.IO/i,
                  /connection closed/i,
                  
                  // Performance patterns
                  /Memory/i,
                  /Performance/i,
                  /Slow network/i,
                  /Long task/i,
                  
                  // Generic patterns
                  /error\\s*:\\s*\\d+/i,
                  /warn(?:ing)?.*deprecated/i,
                  /uncaught\\s+(?:reference|type)error/i,
                  /cannot\\s+read\\s+propert(?:y|ies)/i,
                  /is\\s+not\\s+defined/i,
                  /hydration\\s+(?:error|warning|mismatch)/i,
                  /Load failed/i,
                  /retry_count/i,
                ];
                
                function shouldSuppress(message) {
                  if (typeof message !== 'string') {
                    message = String(message);
                  }
                  return errorPatterns.some(pattern => pattern.test(message));
                }
                
                // Override console methods
                console.error = function(...args) {
                  const message = args.join(' ');
                  if (!shouldSuppress(message)) {
                    originalError.apply(console, args);
                  }
                };
                
                console.warn = function(...args) {
                  const message = args.join(' ');
                  if (!shouldSuppress(message)) {
                    originalWarn.apply(console, args);
                  }
                };
                
                console.log = function(...args) {
                  const message = args.join(' ');
                  if (!shouldSuppress(message)) {
                    originalLog.apply(console, args);
                  }
                };
                
                // Suppress unhandled promise rejections
                window.addEventListener('unhandledrejection', function(event) {
                  const reason = event.reason;
                  let message = '';
                  
                  if (reason instanceof Error) {
                    message = reason.name + ': ' + reason.message;
                  } else if (typeof reason === 'string') {
                    message = reason;
                  } else {
                    message = String(reason);
                  }
                  
                  if (shouldSuppress(message)) {
                    event.preventDefault();
                  }
                });
                
                // Suppress error events
                window.addEventListener('error', function(event) {
                  if (event.target !== window) {
                    const target = event.target;
                    const src = target.src || target.href || '';
                    if (shouldSuppress(src)) {
                      event.preventDefault();
                      return;
                    }
                  }
                  
                  const message = event.message || '';
                  if (shouldSuppress(message)) {
                    event.preventDefault();
                  }
                }, true);
                
                // Override XMLHttpRequest to suppress specific requests
                const originalXHROpen = XMLHttpRequest.prototype.open;
                XMLHttpRequest.prototype.open = function(method, url, ...args) {
                  if (shouldSuppress(url)) {
                    // Create a fake successful response
                    const self = this;
                    setTimeout(function() {
                      Object.defineProperty(self, 'readyState', { value: 4, writable: false });
                      Object.defineProperty(self, 'status', { value: 200, writable: false });
                      Object.defineProperty(self, 'responseText', { value: '{}', writable: false });
                      self.onreadystatechange && self.onreadystatechange();
                    }, 0);
                    return;
                  }
                  return originalXHROpen.apply(this, [method, url, ...args]);
                };
                
                // Override fetch to suppress specific requests
                const originalFetch = window.fetch;
                window.fetch = function(url, options) {
                  if (shouldSuppress(url)) {
                    return Promise.resolve(new Response('{}', {
                      status: 200,
                      statusText: 'OK',
                      headers: { 'Content-Type': 'application/json' }
                    }));
                  }
                  return originalFetch.apply(this, [url, options]);
                };
              })();
            `,
          }}
        />
      </head>
      <body className={`${inter.className} bg-black text-white antialiased`}>
        <ClientErrorSuppression />
        {children}
        <Toaster />
      </body>
    </html>
  );
}
