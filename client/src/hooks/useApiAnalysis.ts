import { useState } from 'react';

export interface AnalysisStep {
  id: string;
  title: string;
  description: string;
  endpoint: string;
  method: 'GET' | 'POST';
  completed: boolean;
  loading: boolean;
  data?: any;
  error?: string;
}

export interface AnalysisState {
  currentStep: number;
  steps: AnalysisStep[];
  isRunning: boolean;
  overallProgress: number;
}

const initialSteps: AnalysisStep[] = [
  {
    id: 'extract',
    title: 'Data Extraction',
    description: 'Extracting data from all 4 PDF folders (PO, Purchase Invoice, GRN, Sales Invoice)',
    endpoint: '/extract/all-documents',
    method: 'POST',
    completed: false,
    loading: false,
  },
  {
    id: 'three-way-matching',
    title: 'Task 1: 3-Way Matching',
    description: 'Verify if PO quantities match GRN quantities and vendor invoices',
    endpoint: '/analytics/matching',
    method: 'GET',
    completed: false,
    loading: false,
  },
  {
    id: 'verification',
    title: 'Task 2: Verification',
    description: 'Excess Short Procurement / excess procurement analysis',
    endpoint: '/verify/po-invoice',
    method: 'POST',
    completed: false,
    loading: false,
  },
  {
    id: 'cost-analysis',
    title: 'Task 3: Inventory Cost Analysis',
    description: 'Carrying Cost analysis for obsolete products & Gross Margin analysis',
    endpoint: '/analyze/inventory-cost',
    method: 'POST',
    completed: false,
    loading: false,
  },
  {
    id: 'ageing-analysis',
    title: 'Task 4: Inventory Ageing Analysis',
    description: 'Obsolete/Dead Stock: Items not sold within shelf life window',
    endpoint: '/analyze/inventory-ageing',
    method: 'POST',
    completed: false,
    loading: false,
  },
  {
    id: 'fifo-valuation',
    title: 'Task 5: Inventory Valuation Analysis',
    description: 'Stock Valuation: Value of inventory based on FIFO vs. selling price',
    endpoint: '/analyze/inventory-valuation',
    method: 'POST',
    completed: false,
    loading: false,
  },
  {
    id: 'profitability',
    title: 'Final Task: Profitability Analysis',
    description: 'Vendor margins, category profitability, SKU gross margins, and top performers',
    endpoint: '/analyze/profitability',
    method: 'POST',
    completed: false,
    loading: false,
  },
];

export const useApiAnalysis = () => {
  const [analysisState, setAnalysisState] = useState<AnalysisState>({
    currentStep: 0,
    steps: initialSteps,
    isRunning: false,
    overallProgress: 0,
  });

  const executeStep = async (stepIndex: number) => {
    const step = analysisState.steps[stepIndex];
    if (!step) return;

    setAnalysisState(prev => ({
      ...prev,
      steps: prev.steps.map((s, i) => 
        i === stepIndex ? { ...s, loading: true, error: undefined } : s
      ),
    }));

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout

      const fetchOptions: RequestInit = {
        method: step.method,
        headers: {
          'Content-Type': 'application/json',
        },
        signal: controller.signal,
      };

      if (step.method === 'POST') {
        fetchOptions.body = JSON.stringify({});
      }

      const response = await fetch(`http://localhost:8000${step.endpoint}`, fetchOptions);

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Server Error (${response.status}): ${errorText}`);
      }

      const data = await response.json();

      setAnalysisState(prev => ({
        ...prev,
        steps: prev.steps.map((s, i) => 
          i === stepIndex 
            ? { ...s, loading: false, completed: true, data, error: undefined }
            : s
        ),
        overallProgress: ((stepIndex + 1) / prev.steps.length) * 100,
      }));

      return data;
    } catch (error) {
      let errorMessage = 'Unknown error occurred';
      
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          errorMessage = 'Request timed out. Please try again.';
        } else if (error.message.includes('Failed to fetch')) {
          errorMessage = 'Cannot connect to backend server. Please ensure the server is running on port 8000.';
        } else {
          errorMessage = error.message;
        }
      }
      
      setAnalysisState(prev => ({
        ...prev,
        steps: prev.steps.map((s, i) => 
          i === stepIndex 
            ? { ...s, loading: false, completed: false, error: errorMessage }
            : s
        ),
      }));

      throw error;
    }
  };

  const executeNextStep = async () => {
    const nextStepIndex = analysisState.currentStep;
    if (nextStepIndex >= analysisState.steps.length) return null;

    try {
      const result = await executeStep(nextStepIndex);
      
      setAnalysisState(prev => ({
        ...prev,
        currentStep: prev.currentStep + 1,
      }));

      return result;
    } catch (error) {
      console.error('Step execution failed:', error);
      throw error;
    }
  };

  const startAnalysis = () => {
    setAnalysisState(prev => ({
      ...prev,
      isRunning: true,
      currentStep: 0,
      overallProgress: 0,
      steps: initialSteps.map(step => ({
        ...step,
        completed: false,
        loading: false,
        data: undefined,
        error: undefined,
      })),
    }));
  };

  const resetAnalysis = () => {
    setAnalysisState({
      currentStep: 0,
      steps: initialSteps.map(step => ({
        ...step,
        completed: false,
        loading: false,
        data: undefined,
        error: undefined,
      })),
      isRunning: false,
      overallProgress: 0,
    });
  };

  const getCurrentStep = () => analysisState.steps[analysisState.currentStep];
  const getCompletedSteps = () => analysisState.steps.filter(step => step.completed);
  const isAnalysisComplete = () => analysisState.steps.every(step => step.completed);
  const hasErrors = () => analysisState.steps.some(step => step.error);

  return {
    analysisState,
    executeNextStep,
    startAnalysis,
    resetAnalysis,
    getCurrentStep,
    getCompletedSteps,
    isAnalysisComplete,
    hasErrors,
  };
};