/**
 * Save Pipeline Dialog
 *
 * Modal dialog for saving pipelines with name, description, category, and tags.
 * Also supports saving as a template.
 */

import { useState, useEffect } from 'react';
import { Save, Bookmark, Tag, FolderOpen } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from './ui';
import { Button, Input, Textarea, Label, Badge } from './ui';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from './ui';

export interface SavePipelineData {
  name: string;
  description: string;
  category: string;
  tags: string[];
  isTemplate: boolean;
}

interface SavePipelineDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSave: (data: SavePipelineData) => void;
  initialData?: Partial<SavePipelineData>;
  isNew?: boolean;
  saving?: boolean;
}

const CATEGORIES = [
  { value: 'custom', label: 'Custom' },
  { value: 'content', label: 'Content Creation' },
  { value: 'salesforce', label: 'Salesforce & CRM' },
  { value: 'analysis', label: 'Analysis & Research' },
  { value: 'integration', label: 'Data & Integration' },
  { value: 'quality', label: 'Quality Assurance' },
];

export function SavePipelineDialog({
  open,
  onOpenChange,
  onSave,
  initialData,
  isNew = false,
  saving = false,
}: SavePipelineDialogProps) {
  const [name, setName] = useState(initialData?.name || '');
  const [description, setDescription] = useState(initialData?.description || '');
  const [category, setCategory] = useState(initialData?.category || 'custom');
  const [tagInput, setTagInput] = useState('');
  const [tags, setTags] = useState<string[]>(initialData?.tags || []);
  const [isTemplate, setIsTemplate] = useState(initialData?.isTemplate || false);

  // Reset form when dialog opens with new data
  useEffect(() => {
    if (open) {
      setName(initialData?.name || '');
      setDescription(initialData?.description || '');
      setCategory(initialData?.category || 'custom');
      setTags(initialData?.tags || []);
      setIsTemplate(initialData?.isTemplate || false);
      setTagInput('');
    }
  }, [open, initialData]);

  const handleAddTag = () => {
    const trimmedTag = tagInput.trim().toLowerCase();
    if (trimmedTag && !tags.includes(trimmedTag)) {
      setTags([...tags, trimmedTag]);
      setTagInput('');
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setTags(tags.filter((t) => t !== tagToRemove));
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddTag();
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    onSave({
      name: name.trim(),
      description: description.trim(),
      category,
      tags,
      isTemplate,
    });
  };

  const isValid = name.trim().length > 0;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Save className="w-5 h-5" />
              {isNew ? 'Create Pipeline' : 'Save Pipeline'}
            </DialogTitle>
            <DialogDescription>
              {isNew
                ? 'Give your new pipeline a name and configure its settings.'
                : 'Update your pipeline details and settings.'}
            </DialogDescription>
          </DialogHeader>

          <div className="grid gap-4 py-4">
            {/* Name */}
            <div className="grid gap-2">
              <Label htmlFor="name" className="text-sm font-medium">
                Name <span className="text-red-500">*</span>
              </Label>
              <Input
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="My Awesome Pipeline"
                autoFocus
              />
            </div>

            {/* Description */}
            <div className="grid gap-2">
              <Label htmlFor="description" className="text-sm font-medium">
                Description
              </Label>
              <Textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="What does this pipeline do?"
                rows={3}
              />
            </div>

            {/* Category */}
            <div className="grid gap-2">
              <Label htmlFor="category" className="text-sm font-medium flex items-center gap-1">
                <FolderOpen className="w-3.5 h-3.5" />
                Category
              </Label>
              <Select value={category} onValueChange={setCategory}>
                <SelectTrigger>
                  <SelectValue placeholder="Select a category" />
                </SelectTrigger>
                <SelectContent>
                  {CATEGORIES.map((cat) => (
                    <SelectItem key={cat.value} value={cat.value}>
                      {cat.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Tags */}
            <div className="grid gap-2">
              <Label htmlFor="tags" className="text-sm font-medium flex items-center gap-1">
                <Tag className="w-3.5 h-3.5" />
                Tags
              </Label>
              <div className="flex gap-2">
                <Input
                  id="tags"
                  value={tagInput}
                  onChange={(e) => setTagInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Add a tag and press Enter"
                  className="flex-1"
                />
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={handleAddTag}
                  disabled={!tagInput.trim()}
                >
                  Add
                </Button>
              </div>
              {tags.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-1">
                  {tags.map((tag) => (
                    <Badge
                      key={tag}
                      variant="secondary"
                      className="cursor-pointer hover:bg-red-100 dark:hover:bg-red-900/30"
                      onClick={() => handleRemoveTag(tag)}
                    >
                      {tag}
                      <span className="ml-1 text-xs">&times;</span>
                    </Badge>
                  ))}
                </div>
              )}
            </div>

            {/* Save as Template */}
            <div className="flex items-center gap-3 p-3 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50">
              <input
                type="checkbox"
                id="isTemplate"
                checked={isTemplate}
                onChange={(e) => setIsTemplate(e.target.checked)}
                className="w-4 h-4 rounded border-slate-300 text-primary-600 focus:ring-primary-500"
              />
              <div className="flex-1">
                <Label
                  htmlFor="isTemplate"
                  className="text-sm font-medium cursor-pointer flex items-center gap-1"
                >
                  <Bookmark className="w-3.5 h-3.5" />
                  Save as Template
                </Label>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                  Templates appear in the template gallery and can be used to create new pipelines.
                </p>
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={saving}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={!isValid || saving}>
              {saving ? 'Saving...' : isNew ? 'Create Pipeline' : 'Save Changes'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

export default SavePipelineDialog;
