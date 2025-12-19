/**
 * Clarification Card Component
 *
 * Interactive card for answering AI clarification questions.
 * Supports multiple questions - collects all answers before submitting.
 */

import { useState } from 'react';
import { HelpCircle, MessageCircle, Check, Send } from 'lucide-react';
import { Button } from '@/components/ui/button';

export interface ClarificationQuestion {
  id: string;
  question: string;
  choices?: Array<{ label: string; value: string }>;
}

interface ClarificationCardProps {
  questions: ClarificationQuestion[];
  onAnswer: (answer: string) => void;
  originalRequest?: string;
}

export function ClarificationCard({ questions, onAnswer, originalRequest }: ClarificationCardProps) {
  // Track selected answers for each question
  const [answers, setAnswers] = useState<Record<string, string>>({});

  if (!questions || questions.length === 0) return null;

  const handleSelectChoice = (questionId: string, choice: string) => {
    setAnswers((prev) => ({ ...prev, [questionId]: choice }));
  };

  const handleSubmitAll = () => {
    // Combine all answers into a single response
    const answerParts = questions.map((q) => {
      const answer = answers[q.id];
      if (answer) {
        // Just send the answers, not the questions
        return answer;
      }
      return null;
    }).filter(Boolean);

    if (answerParts.length > 0) {
      onAnswer(answerParts.join(', '));
    }
  };

  const answeredCount = Object.keys(answers).length;
  const totalQuestions = questions.length;
  const allAnswered = answeredCount === totalQuestions;

  return (
    <div className="rounded-xl border-2 border-violet-200 dark:border-violet-800 bg-gradient-to-br from-violet-50 to-purple-50 dark:from-violet-900/20 dark:to-purple-900/20 overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 border-b border-violet-200 dark:border-violet-800 flex items-center gap-2 bg-violet-100/50 dark:bg-violet-900/30">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-400 to-purple-500 flex items-center justify-center">
          <HelpCircle className="w-4 h-4 text-white" />
        </div>
        <span className="font-medium text-violet-900 dark:text-violet-100">
          {totalQuestions === 1 ? 'Quick question before I proceed' : `${totalQuestions} quick questions before I proceed`}
        </span>
        {totalQuestions > 1 && (
          <span className="ml-auto text-sm text-violet-600 dark:text-violet-400">
            {answeredCount}/{totalQuestions} answered
          </span>
        )}
      </div>

      {/* Content */}
      <div className="p-4 space-y-5">
        {/* Original request context */}
        {originalRequest && (
          <div className="text-sm text-muted-foreground bg-white/50 dark:bg-gray-900/30 rounded-lg p-3 border border-violet-100 dark:border-violet-800/50">
            <div className="flex items-start gap-2">
              <MessageCircle className="w-4 h-4 mt-0.5 flex-shrink-0 text-violet-500" />
              <div>
                <span className="text-xs uppercase tracking-wide text-violet-600 dark:text-violet-400 font-medium">
                  Your request
                </span>
                <p className="mt-1 text-gray-700 dark:text-gray-300 line-clamp-2">{originalRequest}</p>
              </div>
            </div>
          </div>
        )}

        {/* Questions */}
        {questions.map((q, qIdx) => {
          const isAnswered = !!answers[q.id];
          const selectedAnswer = answers[q.id];

          return (
            <div key={q.id} className="space-y-3">
              {/* Question header */}
              <div className="flex items-start gap-2">
                <span className={`flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-sm font-bold ${
                  isAnswered
                    ? 'bg-emerald-100 dark:bg-emerald-900/40 text-emerald-700 dark:text-emerald-300'
                    : 'bg-violet-100 dark:bg-violet-900/40 text-violet-700 dark:text-violet-300'
                }`}>
                  {isAnswered ? <Check className="w-3.5 h-3.5" /> : qIdx + 1}
                </span>
                <p className={`text-base font-medium ${
                  isAnswered
                    ? 'text-gray-500 dark:text-gray-400'
                    : 'text-gray-900 dark:text-gray-100'
                }`}>
                  {q.question}
                </p>
              </div>

              {/* Choices as buttons */}
              {q.choices && q.choices.length > 0 && (
                <div className="flex flex-wrap gap-2 ml-8">
                  {q.choices.map((choice, idx) => {
                    const choiceLabel = choice.label || choice.value;
                    const isSelected = selectedAnswer === choiceLabel;

                    return (
                      <Button
                        key={idx}
                        variant={isSelected ? 'default' : 'outline'}
                        size="sm"
                        onClick={() => handleSelectChoice(q.id, choiceLabel)}
                        className={`h-auto py-2 px-4 text-sm font-medium transition-all ${
                          isSelected
                            ? 'bg-violet-600 hover:bg-violet-700 text-white border-violet-600'
                            : 'bg-white dark:bg-gray-800 hover:bg-violet-100 dark:hover:bg-violet-900/40 hover:border-violet-400 dark:hover:border-violet-500 hover:text-violet-700 dark:hover:text-violet-300'
                        }`}
                      >
                        {isSelected && <Check className="w-3.5 h-3.5 mr-1.5" />}
                        {choiceLabel}
                      </Button>
                    );
                  })}
                </div>
              )}

              {/* No choices - free text hint */}
              {(!q.choices || q.choices.length === 0) && (
                <p className="text-sm text-muted-foreground italic ml-8">
                  Type your answer in the chat input below
                </p>
              )}
            </div>
          );
        })}

        {/* Submit button - only show when there are multiple questions */}
        {totalQuestions > 1 && (
          <div className="pt-3 border-t border-violet-200/50 dark:border-violet-800/50">
            <Button
              onClick={handleSubmitAll}
              disabled={!allAnswered}
              className={`w-full ${
                allAnswered
                  ? 'bg-gradient-to-r from-violet-500 to-purple-600 hover:from-violet-600 hover:to-purple-700 text-white'
                  : 'bg-gray-100 dark:bg-gray-800 text-gray-400 cursor-not-allowed'
              }`}
            >
              <Send className="w-4 h-4 mr-2" />
              {allAnswered ? 'Submit Answers' : `Answer all ${totalQuestions} questions to continue`}
            </Button>
          </div>
        )}

        {/* For single question, auto-submit when clicked */}
        {totalQuestions === 1 && answeredCount === 1 && (
          <div className="pt-3 border-t border-violet-200/50 dark:border-violet-800/50">
            <Button
              onClick={handleSubmitAll}
              className="w-full bg-gradient-to-r from-violet-500 to-purple-600 hover:from-violet-600 hover:to-purple-700 text-white"
            >
              <Send className="w-4 h-4 mr-2" />
              Continue with "{answers[questions[0].id]}"
            </Button>
          </div>
        )}

        {/* Help text */}
        <p className="text-xs text-muted-foreground text-center">
          {totalQuestions > 1
            ? 'Select an answer for each question, then click Submit'
            : 'Click a choice above, then click Continue'}
        </p>
      </div>
    </div>
  );
}
