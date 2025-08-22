/**
 * Health Check Routes
 * 
 * Provides health monitoring and status endpoints for the semantic analysis API.
 */

import { Router, Request, Response } from 'express';

export function setupHealthRoutes(router: Router): void {
  // Basic health check
  router.get('/health', (req: Request, res: Response) => {
    const uptime = process.uptime();
    const memoryUsage = process.memoryUsage();

    res.json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      uptime: {
        seconds: Math.floor(uptime),
        formatted: formatUptime(uptime)
      },
      memory: {
        rss: `${Math.round(memoryUsage.rss / 1024 / 1024)}MB`,
        heapTotal: `${Math.round(memoryUsage.heapTotal / 1024 / 1024)}MB`,
        heapUsed: `${Math.round(memoryUsage.heapUsed / 1024 / 1024)}MB`,
        external: `${Math.round(memoryUsage.external / 1024 / 1024)}MB`
      },
      requestId: req.id
    });
  });

  // Detailed health check
  router.get('/health/detailed', (req: Request, res: Response) => {
    const { cache, searchEngine, patternMatcher } = req.semanticContext;
    
    res.json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      version: process.version,
      platform: process.platform,
      arch: process.arch,
      memory: process.memoryUsage(),
      components: {
        cache: {
          status: 'healthy',
          stats: cache.getStats()
        },
        searchEngine: {
          status: 'healthy',
          stats: searchEngine.getStats()
        },
        patternMatcher: {
          status: 'healthy',
          stats: patternMatcher.getStats()
        }
      },
      requestId: req.id
    });
  });

  // Readiness check
  router.get('/health/ready', (req: Request, res: Response) => {
    try {
      const { cache, searchEngine, patternMatcher } = req.semanticContext;
      
      // Check if all components are ready
      const cacheReady = cache && typeof cache.getStats === 'function';
      const searchReady = searchEngine && typeof searchEngine.getStats === 'function';
      const patternsReady = patternMatcher && typeof patternMatcher.getStats === 'function';

      if (cacheReady && searchReady && patternsReady) {
        res.json({
          status: 'ready',
          timestamp: new Date().toISOString(),
          components: {
            cache: 'ready',
            searchEngine: 'ready',
            patternMatcher: 'ready'
          },
          requestId: req.id
        });
      } else {
        res.status(503).json({
          status: 'not ready',
          timestamp: new Date().toISOString(),
          components: {
            cache: cacheReady ? 'ready' : 'not ready',
            searchEngine: searchReady ? 'ready' : 'not ready',
            patternMatcher: patternsReady ? 'ready' : 'not ready'
          },
          requestId: req.id
        });
      }
    } catch (error) {
      res.status(503).json({
        status: 'error',
        error: error.message,
        timestamp: new Date().toISOString(),
        requestId: req.id
      });
    }
  });

  // Liveness check
  router.get('/health/live', (req: Request, res: Response) => {
    res.json({
      status: 'alive',
      timestamp: new Date().toISOString(),
      pid: process.pid,
      requestId: req.id
    });
  });

  // Performance metrics
  router.get('/health/metrics', (req: Request, res: Response) => {
    const { cache, searchEngine, patternMatcher } = req.semanticContext;
    
    res.json({
      timestamp: new Date().toISOString(),
      metrics: {
        cache: cache.getStats(),
        search: searchEngine.getStats(),
        patterns: patternMatcher.getStats(),
        system: {
          uptime: process.uptime(),
          memory: process.memoryUsage(),
          cpuUsage: process.cpuUsage()
        }
      },
      requestId: req.id
    });
  });
}

function formatUptime(seconds: number): string {
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);

  return `${days}d ${hours}h ${minutes}m ${secs}s`;
}