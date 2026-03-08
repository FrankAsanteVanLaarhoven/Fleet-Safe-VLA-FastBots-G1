# Figma MCP Server for AuraAI

A powerful Model Context Protocol (MCP) server that integrates with AuraAI's website cloning system to extract Figma and other design assets from websites.

## 🚀 Features

- **Figma Link Extraction**: Automatically detect and extract Figma links from any website
- **Design Asset Scanning**: Comprehensive scanning for Figma, Sketch, Adobe, and other design files
- **Component Extraction**: Extract specific components from Figma files using the Figma API
- **File Download**: Download complete Figma files for local use
- **Multi-format Support**: Support for various design file formats and platforms

## 📦 Installation

### Prerequisites
- Node.js 18+ 
- npm or yarn
- Figma Access Token (for private file access)

### Quick Start

1. **Clone the repository**:
```bash
git clone https://github.com/auraai/figma-mcp-server.git
cd figma-mcp-server
```

2. **Install dependencies**:
```bash
npm install
```

3. **Set up Figma Access Token** (optional):
```bash
export FIGMA_ACCESS_TOKEN="your_figma_access_token_here"
```

4. **Start the server**:
```bash
npm start
```

## 🛠️ Available Tools

### 1. Extract Figma Links
Extract all Figma links from a website URL.

```json
{
  "name": "extract_figma_links",
  "arguments": {
    "url": "https://example.com"
  }
}
```

### 2. Download Figma File
Download a complete Figma file using its file key.

```json
{
  "name": "download_figma_file",
  "arguments": {
    "fileKey": "figma_file_key_here",
    "accessToken": "optional_figma_token"
  }
}
```

### 3. Scan Website for Design Assets
Comprehensive scan for all design assets on a website.

```json
{
  "name": "scan_website_for_design_assets",
  "arguments": {
    "url": "https://example.com",
    "depth": 2
  }
}
```

### 4. Extract Figma Components
Extract specific components from a Figma file.

```json
{
  "name": "extract_figma_components",
  "arguments": {
    "fileKey": "figma_file_key_here",
    "nodeIds": ["node_id_1", "node_id_2"],
    "accessToken": "required_figma_token"
  }
}
```

## 🔧 Integration with AuraAI

### 1. Add to AuraAI Configuration

Add the MCP server to your AuraAI configuration:

```json
{
  "mcpServers": {
    "figma-extractor": {
      "command": "node",
      "args": ["/path/to/figma-mcp-server/mcp-server.js"],
      "env": {
        "FIGMA_ACCESS_TOKEN": "your_token_here"
      }
    }
  }
}
```

### 2. Enhanced Website Cloning

When cloning a website, the MCP server will automatically:

1. **Scan for Design Assets**: Detect Figma links and other design files
2. **Extract File Keys**: Parse Figma URLs to extract file keys
3. **Download Assets**: Download design files when possible
4. **Generate Reports**: Create comprehensive design asset reports

### 3. Example Workflow

```javascript
// Example integration with AuraAI cloning process
const figmaResults = await mcpClient.callTool('scan_website_for_design_assets', {
  url: 'https://aura.build/',
  depth: 2
});

// Extract Figma files found
const figmaFiles = figmaResults.content[0].text;
console.log('Found design assets:', figmaFiles);
```

## 📁 Output Structure

The MCP server creates organized output directories:

```
downloads/
├── figma/
│   ├── figma-file-key-1234567890.json
│   └── figma-file-key-0987654321.json
├── figma-components/
│   ├── components-file-key-1234567890.json
│   └── components-file-key-0987654321.json
└── reports/
    ├── design-assets-scan-report.json
    └── figma-extraction-summary.json
```

## 🔐 Authentication

### Figma Access Token

For private Figma files and component extraction, you'll need a Figma access token:

1. Go to [Figma Account Settings](https://www.figma.com/settings)
2. Navigate to "Personal access tokens"
3. Create a new token
4. Set the token as an environment variable:
   ```bash
   export FIGMA_ACCESS_TOKEN="your_token_here"
   ```

### Public Files

Public Figma files can be accessed without authentication, but with limited functionality.

## 🎯 Use Cases

### 1. Website Design Analysis
- Extract design systems from competitor websites
- Analyze UI/UX patterns and components
- Download design assets for reference

### 2. Design Asset Management
- Automatically collect design files from project websites
- Organize design assets by project
- Create design asset inventories

### 3. Development Workflow
- Extract design tokens and components
- Generate code from Figma designs
- Maintain design-to-code synchronization

### 4. Research and Inspiration
- Collect design inspiration from various sources
- Analyze design trends across websites
- Build design pattern libraries

## 🚀 Advanced Features

### 1. Batch Processing
Process multiple websites simultaneously:

```javascript
const websites = [
  'https://website1.com',
  'https://website2.com',
  'https://website3.com'
];

for (const website of websites) {
  const results = await mcpClient.callTool('scan_website_for_design_assets', {
    url: website,
    depth: 1
  });
  console.log(`Results for ${website}:`, results);
}
```

### 2. Custom Filters
Filter design assets by type, size, or other criteria:

```javascript
const results = await mcpClient.callTool('scan_website_for_design_assets', {
  url: 'https://example.com',
  depth: 2
});

// Filter for specific design file types
const figmaFiles = results.content[0].text.match(/figma\.com\/file\/[a-zA-Z0-9]+/g);
```

### 3. Integration with Design Tools
Connect extracted assets to your design workflow:

```javascript
// Extract components and generate design tokens
const components = await mcpClient.callTool('extract_figma_components', {
  fileKey: 'figma_file_key',
  nodeIds: ['component_node_ids'],
  accessToken: 'your_token'
});

// Generate CSS variables from extracted components
const cssVariables = generateCSSFromComponents(components);
```

## 🔧 Configuration Options

### Environment Variables

```bash
# Required for private Figma access
FIGMA_ACCESS_TOKEN=your_token_here

# Optional: Custom download directory
DOWNLOAD_DIR=/custom/path/to/downloads

# Optional: Maximum scan depth
MAX_SCAN_DEPTH=3

# Optional: Request timeout (ms)
REQUEST_TIMEOUT=10000
```

### Server Configuration

```javascript
// Custom server configuration
const serverConfig = {
  name: 'figma-extractor',
  version: '1.0.0',
  capabilities: {
    tools: {},
    resources: {},
  },
  // Custom error handling
  onError: (error) => {
    console.error('MCP Server Error:', error);
  }
};
```

## 🐛 Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Ensure your Figma access token is valid
   - Check token permissions and expiration
   - Verify the file is accessible with your token

2. **Network Timeouts**
   - Increase timeout settings for slow websites
   - Check network connectivity
   - Verify website accessibility

3. **Rate Limiting**
   - Implement delays between requests
   - Use proper User-Agent headers
   - Respect website robots.txt

### Debug Mode

Enable debug logging:

```bash
DEBUG=figma-mcp-server:* npm start
```

## 📈 Performance Optimization

### 1. Parallel Processing
Process multiple URLs concurrently:

```javascript
const urls = ['url1', 'url2', 'url3'];
const promises = urls.map(url => 
  mcpClient.callTool('extract_figma_links', { url })
);
const results = await Promise.all(promises);
```

### 2. Caching
Implement caching for repeated requests:

```javascript
const cache = new Map();

async function cachedExtract(url) {
  if (cache.has(url)) {
    return cache.get(url);
  }
  
  const result = await mcpClient.callTool('extract_figma_links', { url });
  cache.set(url, result);
  return result;
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

- **Documentation**: [GitHub Wiki](https://github.com/auraai/figma-mcp-server/wiki)
- **Issues**: [GitHub Issues](https://github.com/auraai/figma-mcp-server/issues)
- **Discussions**: [GitHub Discussions](https://github.com/auraai/figma-mcp-server/discussions)

## 🔗 Related Projects

- [AuraAI Website Cloner](https://github.com/auraai/website-cloner)
- [Design Token Extractor](https://github.com/auraai/design-token-extractor)
- [Figma to Code Generator](https://github.com/auraai/figma-to-code)

---

**Built with ❤️ by the AuraAI Team** 