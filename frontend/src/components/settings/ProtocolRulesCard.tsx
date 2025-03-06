import React, { useState } from "react";
import { FiList, FiPlus, FiEdit2, FiTrash2, FiSave, FiX } from "react-icons/fi";
import { configService } from "../../client/services/config";
import type { IProtocolPortMappingRule } from "../../client/api/models/request";
import { useMutation, useQuery } from "react-query";

const RuleEditor: React.FC<{
  rule: IProtocolPortMappingRule;
  onSave: (rule: IProtocolPortMappingRule) => void;
  onCancel: () => void;
  onChange: (rule: IProtocolPortMappingRule) => void;
}> = ({ rule, onSave, onCancel, onChange }) => {
  return (
    <div className="flex items-center gap-4 rounded-lg bg-gray-50 p-4 dark:bg-gray-700">
      <input
        type="number"
        className="w-24 rounded-lg border border-gray-200 bg-white px-3 py-2 dark:border-gray-600 dark:bg-gray-800"
        value={rule.port.port}
        onChange={(e) => {
          const port = parseInt(e.target.value);
          if (port >= 1 && port <= 65535) {
            onChange({ ...rule, port: { port } });
          }
        }}
        min={1}
        max={65535}
      />
      <input
        type="text"
        className="flex-1 rounded-lg border border-gray-200 bg-white px-3 py-2 dark:border-gray-600 dark:bg-gray-800"
        value={rule.protocol}
        onChange={(e) => onChange({ ...rule, protocol: e.target.value })}
      />
      <button
        onClick={() => onSave(rule)}
        className="rounded-lg bg-blue-500 p-2 text-white hover:bg-blue-600"
      >
        <FiSave className="h-5 w-5" />
      </button>
      <button
        onClick={onCancel}
        className="rounded-lg bg-gray-500 p-2 text-white hover:bg-gray-600"
      >
        <FiX className="h-5 w-5" />
      </button>
    </div>
  );
};

const ProtocolRulesCard: React.FC = () => {
  const [rules, setRules] = useState<IProtocolPortMappingRule[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [editingRule, setEditingRule] = useState<IProtocolPortMappingRule | null>(
    null
  );
  const [editingRuleState, setEditingRuleState] = useState<IProtocolPortMappingRule | null>(
    null
  );
  const [newRule, setNewRule] = useState<IProtocolPortMappingRule | null>(null);

  const query = useQuery({
    queryKey: "rules",
    queryFn: configService.getRules,
    onSuccess: (data) => {
      setRules(data.rules);
    },
    onError: (error) => {
      console.error("Failed to load rules:", error);
      setError("Failed to load rules");
    },
    refetchInterval: false,
    retry: 3,
  });

  const mutationAdd = useMutation({
    mutationKey: "addOrUpdateRule",
    mutationFn: configService.addOrUpdateRule,
    onSuccess: (data) => {
      setRules(data.rules);
    },
    onError: (error) => {
      console.error("Failed to save rule:", error);
      setError("Failed to save rule");
    },
  });

  const mutationDelete = useMutation({
    mutationKey: "deleteRule",
    mutationFn: configService.deleteRule,
    onSuccess: (data) => {
      setRules(data.rules);
    },
    onError: (error) => {
      console.error("Failed to delete rule:", error);
      setError("Failed to delete rule");
    },
  });

  const handleAddRule = () => {
    const newRuleData = {
      port: { port: 80 },
      protocol: "HTTP",
    };
    setNewRule(newRuleData);
    setEditingRuleState(newRuleData);
  };

  const handleSaveRule = async (rule: IProtocolPortMappingRule) => {
    try {
      await mutationAdd.mutateAsync(rule);
      setEditingRule(null);
      setEditingRuleState(null);
      setNewRule(null);
    } catch (error) {
      console.error("Failed to save rule:", error);
    }
  };

  const handleDeleteRule = async (rule: IProtocolPortMappingRule) => {
    try {
      await mutationDelete.mutateAsync(rule);
    } catch (error) {
      console.error("Failed to delete rule:", error);
    }
  };

  const handleEditRule = (rule: IProtocolPortMappingRule) => {
    setEditingRule(rule);
    setEditingRuleState({ ...rule });
  };

  const handleRuleChange = (rule: IProtocolPortMappingRule) => {
    setEditingRuleState(rule);
  };

  return (
    <div className="flex h-48 flex-col rounded-xl bg-white p-6 shadow-lg transition-all duration-300 hover:shadow-xl dark:bg-gray-800">
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-purple-500 to-purple-600">
            <FiList className="h-6 w-6 text-white" />
          </div>
          <h3 className="text-lg font-semibold text-gray-800 dark:text-white">
            Protocol-Port Rules
          </h3>
        </div>
        <button
          onClick={handleAddRule}
          className="flex items-center gap-2 rounded-lg bg-purple-500 px-4 py-2 text-white hover:bg-purple-600"
        >
          <FiPlus className="h-5 w-5" />
          Add Rule
        </button>
      </div>

      {query.isLoading ? (
        <div className="animate-pulse space-y-3">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="h-12 w-full rounded-lg bg-gray-200 dark:bg-gray-700"
            />
          ))}
        </div>
      ) : query.isError ? (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-600 dark:border-red-900 dark:bg-red-900/20 dark:text-red-400">
          {error}
        </div>
      ) : (
        <div className="space-y-3 overflow-y-auto">
          {newRule && editingRuleState && (
            <RuleEditor
              rule={editingRuleState}
              onSave={handleSaveRule}
              onCancel={() => {
                setNewRule(null);
                setEditingRuleState(null);
              }}
              onChange={handleRuleChange}
            />
          )}
          {rules.map((rule) =>
            editingRule?.port.port === rule.port.port ? (
              <RuleEditor
                key={rule.port.port}
                rule={editingRuleState || rule}
                onSave={handleSaveRule}
                onCancel={() => {
                  setEditingRule(null);
                  setEditingRuleState(null);
                }}
                onChange={handleRuleChange}
              />
            ) : (
              <div
                key={rule.port.port}
                className="flex items-center justify-between rounded-lg bg-gray-50 p-4 dark:bg-gray-700"
              >
                <div className="flex items-center gap-4">
                  <span className="text-sm font-medium text-gray-500 dark:text-gray-400">
                    Port:
                  </span>
                  <span className="font-mono text-gray-900 dark:text-white">
                    {rule.port.port}
                  </span>
                  <span className="text-sm font-medium text-gray-500 dark:text-gray-400">
                    Protocol:
                  </span>
                  <span className="font-mono text-gray-900 dark:text-white">
                    {rule.protocol}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleEditRule(rule)}
                    className="rounded-lg p-2 text-gray-500 hover:bg-gray-200 hover:text-gray-700 dark:text-gray-400 dark:hover:bg-gray-600 dark:hover:text-gray-200"
                  >
                    <FiEdit2 className="h-5 w-5" />
                  </button>
                  <button
                    onClick={() => handleDeleteRule(rule)}
                    className="rounded-lg p-2 text-red-500 hover:bg-red-100 hover:text-red-700 dark:hover:bg-red-900"
                  >
                    <FiTrash2 className="h-5 w-5" />
                  </button>
                </div>
              </div>
            )
          )}
        </div>
      )}
    </div>
  );
};

export default ProtocolRulesCard;
