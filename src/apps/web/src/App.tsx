import React, { Suspense } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Box, CircularProgress } from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';

// Layout components
import MainLayout from '@components/layout/MainLayout';
import LoadingSpinner from '@components/ui/LoadingSpinner';

// Lazy load pages for code splitting
const Dashboard = React.lazy(() => import('@pages/dashboard/Dashboard'));
const Chat = React.lazy(() => import('@pages/chat/Chat'));
const Documentation = React.lazy(() => import('@pages/docs/Documentation'));
const Components = React.lazy(() => import('@pages/components/Components'));
const Settings = React.lazy(() => import('@pages/settings/Settings'));
const FileExplorerPage = React.lazy(() => import('@pages/fileExplorer/FileExplorerPage').then(module => ({ default: module.FileExplorerPage })));

// Page transition variants
const pageVariants = {
  initial: { opacity: 0, x: -20 },
  in: { opacity: 1, x: 0 },
  out: { opacity: 0, x: 20 }
};

const pageTransition = {
  type: "tween",
  ease: "anticipate",
  duration: 0.3
};

function App() {
  return (
    <MainLayout>
      <AnimatePresence mode="wait">
        <Routes>
          <Route 
            path="/" 
            element={<Navigate to="/dashboard" replace />} 
          />
          <Route 
            path="/dashboard" 
            element={
              <motion.div
                initial="initial"
                animate="in"
                exit="out"
                variants={pageVariants}
                transition={pageTransition}
              >
                <Suspense fallback={<LoadingSpinner />}>
                  <Dashboard />
                </Suspense>
              </motion.div>
            } 
          />
          <Route 
            path="/chat" 
            element={
              <motion.div
                initial="initial"
                animate="in"
                exit="out"
                variants={pageVariants}
                transition={pageTransition}
              >
                <Suspense fallback={<LoadingSpinner />}>
                  <Chat />
                </Suspense>
              </motion.div>
            } 
          />
          <Route 
            path="/docs/*" 
            element={
              <motion.div
                initial="initial"
                animate="in"
                exit="out"
                variants={pageVariants}
                transition={pageTransition}
              >
                <Suspense fallback={<LoadingSpinner />}>
                  <Documentation />
                </Suspense>
              </motion.div>
            } 
          />
          <Route 
            path="/components/*" 
            element={
              <motion.div
                initial="initial"
                animate="in"
                exit="out"
                variants={pageVariants}
                transition={pageTransition}
              >
                <Suspense fallback={<LoadingSpinner />}>
                  <Components />
                </Suspense>
              </motion.div>
            } 
          />
          <Route 
            path="/settings" 
            element={
              <motion.div
                initial="initial"
                animate="in"
                exit="out"
                variants={pageVariants}
                transition={pageTransition}
              >
                <Suspense fallback={<LoadingSpinner />}>
                  <Settings />
                </Suspense>
              </motion.div>
            } 
          />
          <Route 
            path="/file-explorer" 
            element={
              <motion.div
                initial="initial"
                animate="in"
                exit="out"
                variants={pageVariants}
                transition={pageTransition}
              >
                <Suspense fallback={<LoadingSpinner />}>
                  <FileExplorerPage />
                </Suspense>
              </motion.div>
            } 
          />
          <Route 
            path="*" 
            element={<Navigate to="/dashboard" replace />} 
          />
        </Routes>
      </AnimatePresence>
    </MainLayout>
  );
}

export default App;