#!/usr/bin/env node

const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const { CallToolRequestSchema, ListToolsRequestSchema } = require('@modelcontextprotocol/sdk/types.js');
const axios = require('axios');
const cheerio = require('cheerio');
const fs = require('fs').promises;
const path = require('path');

class FigmaMCPServer {
  constructor() {
    this.server = new Server(
      {
        name: 'figma-extractor',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupToolHandlers();
  }

  setupToolHandlers() {
    // List available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          {
            name: 'extract_figma_links',
            description: 'Extract Figma links from a website URL',
            inputSchema: {
              type: 'object',
              properties: {
                url: {
                  type: 'string',
                  description: 'The website URL to scan for Figma links',
                },
              },
              required: ['url'],
            },
          },
          {
            name: 'download_figma_file',
            description: 'Download a Figma file using its file key',
            inputSchema: {
              type: 'object',
              properties: {
                fileKey: {
                  type: 'string',
                  description: 'The Figma file key to download',
                },
                accessToken: {
                  type: 'string',
                  description: 'Figma access token (optional)',
                },
              },
              required: ['fileKey'],
            },
          },
          {
            name: 'scan_website_for_design_assets',
            description: 'Comprehensive scan for design assets including Figma, Sketch, and other design files',
            inputSchema: {
              type: 'object',
              properties: {
                url: {
                  type: 'string',
                  description: 'The website URL to scan',
                },
                depth: {
                  type: 'number',
                  description: 'Scan depth (1-3, default: 2)',
                  default: 2,
                },
              },
              required: ['url'],
            },
          },
          {
            name: 'extract_figma_components',
            description: 'Extract specific components from a Figma file',
            inputSchema: {
              type: 'object',
              properties: {
                fileKey: {
                  type: 'string',
                  description: 'The Figma file key',
                },
                nodeIds: {
                  type: 'array',
                  items: { type: 'string' },
                  description: 'Array of node IDs to extract',
                },
                accessToken: {
                  type: 'string',
                  description: 'Figma access token',
                },
              },
              required: ['fileKey', 'nodeIds'],
            },
          },
        ],
      };
    });

    // Handle tool calls
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case 'extract_figma_links':
            return await this.extractFigmaLinks(args.url);
          
          case 'download_figma_file':
            return await this.downloadFigmaFile(args.fileKey, args.accessToken);
          
          case 'scan_website_for_design_assets':
            return await this.scanWebsiteForDesignAssets(args.url, args.depth || 2);
          
          case 'extract_figma_components':
            return await this.extractFigmaComponents(args.fileKey, args.nodeIds, args.accessToken);
          
          default:
            throw new Error(`Unknown tool: ${name}`);
        }
      } catch (error) {
        return {
          content: [
            {
              type: 'text',
              text: `Error: ${error.message}`,
            },
          ],
        };
      }
    });
  }

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
        content: [
          {
            type: 'text',
            text: `Found ${figmaLinks.length} Figma links on ${url}:\n\n${figmaLinks.map((link, i) => 
              `${i + 1}. ${link.text}\n   URL: ${link.url}\n   Context: ${link.context}\n`
            ).join('\n')}\n\nFile Keys: ${fileKeys.join(', ')}`,
          },
        ],
      };
    } catch (error) {
      throw new Error(`Failed to extract Figma links: ${error.message}`);
    }
  }

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
      
      // Create downloads directory if it doesn't exist
      const downloadsDir = path.join(process.cwd(), 'downloads', 'figma');
      await fs.mkdir(downloadsDir, { recursive: true });

      // Save the file
      const fileName = `figma-${fileKey}-${Date.now()}.json`;
      const filePath = path.join(downloadsDir, fileName);
      
      await fs.writeFile(filePath, JSON.stringify(response.data, null, 2));

      return {
        content: [
          {
            type: 'text',
            text: `✅ Successfully downloaded Figma file ${fileKey}\nSaved to: ${filePath}\nFile size: ${JSON.stringify(response.data).length} bytes`,
          },
        ],
      };
    } catch (error) {
      throw new Error(`Failed to download Figma file: ${error.message}`);
    }
  }

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

      const summary = `
🎨 Design Assets Found on ${url}:

📊 Figma Files: ${designAssets.figma.length}
📊 Sketch Files: ${designAssets.sketch.length}
📊 Adobe Files: ${designAssets.adobe.length}
📊 Other Design Files: ${designAssets.other.length}

${designAssets.figma.length > 0 ? `\n🎯 Figma Files:\n${designAssets.figma.map(f => `- ${f.text} (${f.url})`).join('\n')}` : ''}
${designAssets.sketch.length > 0 ? `\n🎨 Sketch Files:\n${designAssets.sketch.map(f => `- ${f.text} (${f.url})`).join('\n')}` : ''}
${designAssets.adobe.length > 0 ? `\n🎭 Adobe Files:\n${designAssets.adobe.map(f => `- ${f.text} (${f.url})`).join('\n')}` : ''}
${designAssets.other.length > 0 ? `\n📁 Other Design Files:\n${designAssets.other.map(f => `- ${f.text} (${f.url})`).join('\n')}` : ''}
      `;

      return {
        content: [
          {
            type: 'text',
            text: summary,
          },
        ],
      };
    } catch (error) {
      throw new Error(`Failed to scan website: ${error.message}`);
    }
  }

  async extractFigmaComponents(fileKey, nodeIds, accessToken) {
    try {
      console.log(`🔧 Extracting components from Figma file: ${fileKey}`);
      
      if (!accessToken) {
        throw new Error('Access token required for component extraction');
      }

      const components = [];
      
      for (const nodeId of nodeIds) {
        try {
          const response = await axios.get(
            `https://api.figma.com/v1/files/${fileKey}/nodes?ids=${nodeId}`,
            {
              headers: {
                'X-Figma-Token': accessToken,
              },
            }
          );

          if (response.data.nodes[nodeId]) {
            components.push({
              nodeId,
              name: response.data.nodes[nodeId].document.name,
              type: response.data.nodes[nodeId].document.type,
              data: response.data.nodes[nodeId],
            });
          }
        } catch (error) {
          console.log(`⚠️ Failed to extract node ${nodeId}: ${error.message}`);
        }
      }

      // Save extracted components
      const downloadsDir = path.join(process.cwd(), 'downloads', 'figma-components');
      await fs.mkdir(downloadsDir, { recursive: true });

      const fileName = `components-${fileKey}-${Date.now()}.json`;
      const filePath = path.join(downloadsDir, fileName);
      
      await fs.writeFile(filePath, JSON.stringify(components, null, 2));

      return {
        content: [
          {
            type: 'text',
            text: `✅ Successfully extracted ${components.length} components from Figma file ${fileKey}\nSaved to: ${filePath}\n\nComponents:\n${components.map(c => `- ${c.name} (${c.type})`).join('\n')}`,
          },
        ],
      };
    } catch (error) {
      throw new Error(`Failed to extract components: ${error.message}`);
    }
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.log('🚀 Figma MCP Server started');
  }
}

// Start the server
const server = new FigmaMCPServer();
server.run().catch(console.error); 