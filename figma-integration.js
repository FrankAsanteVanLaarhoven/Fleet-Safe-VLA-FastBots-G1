#!/usr/bin/env node

/**
 * Figma Integration Script for AuraAI
 * 
 * This script demonstrates how to integrate the Figma MCP server
 * with the main AuraAI website cloning system.
 */

const axios = require('axios');
const cheerio = require('cheerio');
const fs = require('fs').promises;
const path = require('path');

class FigmaIntegration {
  constructor() {
    this.downloadsDir = path.join(process.cwd(), 'downloads');
    this.figmaDir = path.join(this.downloadsDir, 'figma');
    this.reportsDir = path.join(this.downloadsDir, 'reports');
  }

  async initialize() {
    // Create necessary directories
    await fs.mkdir(this.downloadsDir, { recursive: true });
    await fs.mkdir(this.figmaDir, { recursive: true });
    await fs.mkdir(this.reportsDir, { recursive: true });
  }

  /**
   * Extract Figma links from a website
   */
  async extractFigmaLinks(url) {
    try {
      console.log(`🔍 Scanning ${url} for Figma links...`);
      
      const response = await axios.get(url, {
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        },
        timeout: 10000,
      });

      const $ = cheerio.load(response.data);
      const figmaLinks = [];

      // Find Figma links in various formats
      $('a[href*="figma.com"]').each((i, element) => {
        const href = $(element).attr('href');
        if (href && href.includes('figma.com')) {
          figmaLinks.push({
            url: href,
            text: $(element).text().trim(),
            context: $(element).parent().text().substring(0, 100),
          });
        }
      });

      // Also check for embedded Figma iframes
      $('iframe[src*="figma.com"]').each((i, element) => {
        const src = $(element).attr('src');
        if (src && src.includes('figma.com')) {
          figmaLinks.push({
            url: src,
            text: 'Embedded Figma Design',
            context: 'iframe embed',
          });
        }
      });

      // Extract file keys from URLs
      const fileKeys = figmaLinks.map(link => {
        const match = link.url.match(/figma\.com\/file\/([a-zA-Z0-9]+)/);
        return match ? match[1] : null;
      }).filter(Boolean);

      return {
        links: figmaLinks,
        fileKeys: fileKeys,
        summary: `Found ${figmaLinks.length} Figma links with ${fileKeys.length} unique file keys`
      };
    } catch (error) {
      throw new Error(`Failed to extract Figma links: ${error.message}`);
    }
  }

  /**
   * Download a Figma file using its file key
   */
  async downloadFigmaFile(fileKey, accessToken = null) {
    try {
      console.log(`📥 Downloading Figma file: ${fileKey}`);
      
      // If no access token provided, try to get public file
      const url = accessToken 
        ? `https://api.figma.com/v1/files/${fileKey}`
        : `https://www.figma.com/file/${fileKey}`;

      const headers = accessToken ? {
        'X-Figma-Token': accessToken,
      } : {};

      const response = await axios.get(url, { headers });
      
      // Save the file
      const fileName = `figma-${fileKey}-${Date.now()}.json`;
      const filePath = path.join(this.figmaDir, fileName);
      
      await fs.writeFile(filePath, JSON.stringify(response.data, null, 2));

      return {
        success: true,
        filePath: filePath,
        fileSize: JSON.stringify(response.data).length,
        fileName: fileName
      };
    } catch (error) {
      throw new Error(`Failed to download Figma file: ${error.message}`);
    }
  }

  /**
   * Comprehensive scan for design assets
   */
  async scanWebsiteForDesignAssets(url, depth = 2) {
    try {
      console.log(`🔍 Scanning ${url} for design assets (depth: ${depth})...`);
      
      const visited = new Set();
      const designAssets = {
        figma: [],
        sketch: [],
        adobe: [],
        other: [],
      };

      const scanPage = async (pageUrl, currentDepth) => {
        if (currentDepth > depth || visited.has(pageUrl)) return;
        visited.add(pageUrl);

        try {
          const response = await axios.get(pageUrl, {
            headers: {
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            },
            timeout: 5000,
          });

          const $ = cheerio.load(response.data);

          // Scan for various design file types
          $('a[href]').each((i, element) => {
            const href = $(element).attr('href');
            const text = $(element).text().toLowerCase();

            if (href.includes('figma.com')) {
              designAssets.figma.push({
                url: href,
                page: pageUrl,
                text: $(element).text(),
              });
            } else if (href.includes('.sketch') || text.includes('sketch')) {
              designAssets.sketch.push({
                url: href,
                page: pageUrl,
                text: $(element).text(),
              });
            } else if (href.includes('.ai') || href.includes('.psd') || href.includes('.xd')) {
              designAssets.adobe.push({
                url: href,
                page: pageUrl,
                text: $(element).text(),
              });
            } else if (text.includes('design') || text.includes('mockup') || text.includes('prototype')) {
              designAssets.other.push({
                url: href,
                page: pageUrl,
                text: $(element).text(),
              });
            }
          });

          // If we haven't reached max depth, scan linked pages
          if (currentDepth < depth) {
            const baseUrl = new URL(pageUrl).origin;
            const links = $('a[href^="/"]').slice(0, 5); // Limit to 5 internal links
            
            for (let i = 0; i < links.length; i++) {
              const link = $(links[i]).attr('href');
              if (link) {
                const fullUrl = `${baseUrl}${link}`;
                await scanPage(fullUrl, currentDepth + 1);
              }
            }
          }
        } catch (error) {
          console.log(`⚠️ Failed to scan ${pageUrl}: ${error.message}`);
        }
      };

      await scanPage(url, 0);

      // Save scan report
      const reportFileName = `design-assets-scan-${Date.now()}.json`;
      const reportPath = path.join(this.reportsDir, reportFileName);
      
      await fs.writeFile(reportPath, JSON.stringify({
        url: url,
        scanDate: new Date().toISOString(),
        depth: depth,
        assets: designAssets,
        summary: {
          totalFigma: designAssets.figma.length,
          totalSketch: designAssets.sketch.length,
          totalAdobe: designAssets.adobe.length,
          totalOther: designAssets.other.length,
        }
      }, null, 2));

      return {
        assets: designAssets,
        reportPath: reportPath,
        summary: `Found ${designAssets.figma.length} Figma, ${designAssets.sketch.length} Sketch, ${designAssets.adobe.length} Adobe, and ${designAssets.other.length} other design files`
      };
    } catch (error) {
      throw new Error(`Failed to scan website: ${error.message}`);
    }
  }

  /**
   * Generate a comprehensive design assets report
   */
  async generateDesignReport(url, scanResults) {
    try {
      const report = {
        url: url,
        generatedAt: new Date().toISOString(),
        summary: {
          totalDesignFiles: scanResults.assets.figma.length + 
                           scanResults.assets.sketch.length + 
                           scanResults.assets.adobe.length + 
                           scanResults.assets.other.length,
          figmaFiles: scanResults.assets.figma.length,
          sketchFiles: scanResults.assets.sketch.length,
          adobeFiles: scanResults.assets.adobe.length,
          otherFiles: scanResults.assets.other.length,
        },
        recommendations: [],
        nextSteps: []
      };

      // Generate recommendations based on findings
      if (scanResults.assets.figma.length > 0) {
        report.recommendations.push({
          type: 'figma',
          message: `Found ${scanResults.assets.figma.length} Figma files. Consider extracting design tokens and components.`,
          priority: 'high'
        });
        report.nextSteps.push('Download Figma files using file keys');
        report.nextSteps.push('Extract design tokens and components');
      }

      if (scanResults.assets.sketch.length > 0) {
        report.recommendations.push({
          type: 'sketch',
          message: `Found ${scanResults.assets.sketch.length} Sketch files. Consider converting to Figma or extracting assets.`,
          priority: 'medium'
        });
      }

      if (scanResults.assets.adobe.length > 0) {
        report.recommendations.push({
          type: 'adobe',
          message: `Found ${scanResults.assets.adobe.length} Adobe files. Consider extracting vector assets and design elements.`,
          priority: 'medium'
        });
      }

      // Save the report
      const reportFileName = `design-report-${Date.now()}.json`;
      const reportPath = path.join(this.reportsDir, reportFileName);
      
      await fs.writeFile(reportPath, JSON.stringify(report, null, 2));

      return {
        report: report,
        reportPath: reportPath
      };
    } catch (error) {
      throw new Error(`Failed to generate design report: ${error.message}`);
    }
  }

  /**
   * Main integration function for AuraAI
   */
  async integrateWithAuraAI(websiteUrl, options = {}) {
    try {
      console.log('🚀 Starting Figma integration with AuraAI...');
      
      await this.initialize();

      // Step 1: Scan for design assets
      console.log('📊 Step 1: Scanning for design assets...');
      const scanResults = await this.scanWebsiteForDesignAssets(websiteUrl, options.depth || 2);
      
      // Step 2: Extract Figma links specifically
      console.log('🎯 Step 2: Extracting Figma links...');
      const figmaResults = await this.extractFigmaLinks(websiteUrl);
      
      // Step 3: Download Figma files if requested
      const downloadedFiles = [];
      if (options.downloadFigmaFiles && figmaResults.fileKeys.length > 0) {
        console.log('📥 Step 3: Downloading Figma files...');
        for (const fileKey of figmaResults.fileKeys.slice(0, options.maxDownloads || 5)) {
          try {
            const downloadResult = await this.downloadFigmaFile(fileKey, options.figmaToken);
            downloadedFiles.push(downloadResult);
          } catch (error) {
            console.log(`⚠️ Failed to download ${fileKey}: ${error.message}`);
          }
        }
      }

      // Step 4: Generate comprehensive report
      console.log('📋 Step 4: Generating design report...');
      const designReport = await this.generateDesignReport(websiteUrl, scanResults);

      // Step 5: Create integration summary
      const integrationSummary = {
        websiteUrl: websiteUrl,
        scanDate: new Date().toISOString(),
        scanResults: scanResults,
        figmaResults: figmaResults,
        downloadedFiles: downloadedFiles,
        designReport: designReport,
        summary: {
          totalDesignFiles: scanResults.assets.figma.length + 
                           scanResults.assets.sketch.length + 
                           scanResults.assets.adobe.length + 
                           scanResults.assets.other.length,
          figmaFilesFound: figmaResults.links.length,
          figmaFilesDownloaded: downloadedFiles.length,
          reportsGenerated: 2 // scan report + design report
        }
      };

      // Save integration summary
      const summaryFileName = `integration-summary-${Date.now()}.json`;
      const summaryPath = path.join(this.reportsDir, summaryFileName);
      await fs.writeFile(summaryPath, JSON.stringify(integrationSummary, null, 2));

      console.log('✅ Figma integration completed successfully!');
      console.log(`📊 Summary: ${integrationSummary.summary.totalDesignFiles} design files found`);
      console.log(`🎯 Figma files: ${integrationSummary.summary.figmaFilesFound} found, ${integrationSummary.summary.figmaFilesDownloaded} downloaded`);
      console.log(`📁 Reports saved to: ${this.reportsDir}`);

      return integrationSummary;

    } catch (error) {
      console.error('❌ Figma integration failed:', error.message);
      throw error;
    }
  }
}

// Example usage
async function main() {
  const figmaIntegration = new FigmaIntegration();
  
  try {
    // Example: Integrate with AuraAI for a website
    const results = await figmaIntegration.integrateWithAuraAI('https://aura.build/', {
      depth: 2,
      downloadFigmaFiles: true,
      maxDownloads: 3,
      figmaToken: process.env.FIGMA_ACCESS_TOKEN // Optional
    });

    console.log('🎉 Integration completed!');
    console.log('📊 Results:', JSON.stringify(results.summary, null, 2));
    
  } catch (error) {
    console.error('❌ Integration failed:', error.message);
  }
}

// Export for use in other modules
module.exports = FigmaIntegration;

// Run if called directly
if (require.main === module) {
  main();
} 