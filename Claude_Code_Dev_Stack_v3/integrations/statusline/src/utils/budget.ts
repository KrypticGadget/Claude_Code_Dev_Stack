export interface BudgetStatus {
  percentage: number | null;
  isWarning: boolean;
  displayText: string;
}

export function calculateBudgetPercentage(
  cost: number,
  budget: number | undefined
): number | null {
  if (!budget || budget <= 0 || cost < 0) return null;
  return Math.min(100, (cost / budget) * 100);
}

export function getBudgetStatus(
  cost: number,
  budget: number | undefined,
  warningThreshold = 80
): BudgetStatus {
  const percentage = calculateBudgetPercentage(cost, budget);

  if (percentage === null) {
    return {
      percentage: null,
      isWarning: false,
      displayText: "",
    };
  }

  const percentStr = `${percentage.toFixed(0)}%`;
  const isWarning = percentage >= warningThreshold;

  let displayText = "";
  if (isWarning) {
    displayText = ` !${percentStr}`;
  } else if (percentage >= 50) {
    displayText = ` +${percentStr}`;
  } else {
    displayText = ` ${percentStr}`;
  }

  return {
    percentage,
    isWarning,
    displayText,
  };
}
