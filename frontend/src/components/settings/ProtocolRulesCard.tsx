import React, { useState } from "react";
import { FiList, FiPlus, FiEdit2, FiTrash2, FiSave, FiX } from "react-icons/fi";
import { configService } from "../../client/services/config";
import type { IProtocolPortMappingRule } from "../../client/api/models/request";
import { useMutation, useQuery } from "react-query";

interface IEditingRule {
  protocol: string;
  portsString: string;
}

const RuleEditor: React.FC<{
  rule: IEditingRule;
  onSave: () => void;
  onCancel: () => void;
  onChange: (rule: IEditingRule) => void;
}> = ({ rule, onSave, onCancel, onChange }) => {
  return (
    <div className="flex items-center gap-4 rounded-lg bg-gray-50 p-4 dark:bg-gray-700">
      <input
        type="text"
        className="w-40 rounded-lg border border-gray-200 bg-white px-3 py-2 dark:border-gray-600 dark:bg-gray-800"
        value={rule.portsString}
        onChange={(e) => onChange({ ...rule, portsString: e.target.value })}
        placeholder="e.g. 80, 443"
      />
      <input
        type="text"
        className="flex-1 rounded-lg border border-gray-200 bg-white px-3 py-2 dark:border-gray-600 dark:bg-gray-800"
        value={rule.protocol}
        onChange={(e) => onChange({ ...rule, protocol: e.target.value })}
        placeholder="e.g. HTTP, HTTPS"
      />
      <button
        onClick={onSave}
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
  const [editingRuleState, setEditingRuleState] = useState<IEditingRule | null>(
    null
  );
  const [newRule, setNewRule] = useState<boolean>(false);

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
    setNewRule(true);
    setEditingRuleState({
      protocol: "HTTP",
      portsString: "80",
    });
  };

  const handleSaveRule = async () => {
    if (!editingRuleState) return;

    try {
      const ports = editingRuleState.portsString
        .split(",")
        .map((p) => parseInt(p.trim()))
        .filter((p) => !isNaN(p) && p >= 1 && p <= 65535);

      if (ports.length === 0) {
        setError("At least one valid port is required");
        return;
      }

      await mutationAdd.mutateAsync({
        protocol: editingRuleState.protocol,
        ports,
      });

      setEditingRule(null);
      setEditingRuleState(null);
      setNewRule(false);
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
    setEditingRuleState({
      protocol: rule.protocol,
      portsString: rule.ports.join(", "),
    });
  };

  const handleRuleChange = (rule: IEditingRule) => {
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
                setNewRule(false);
                setEditingRuleState(null);
              }}
              onChange={handleRuleChange}
            />
          )}
          {rules.map((rule) =>
            editingRule?.protocol === rule.protocol &&
            JSON.stringify(editingRule.ports) === JSON.stringify(rule.ports) ? (
              <RuleEditor
                key={`${rule.protocol}-${rule.ports.join(",")}`}
                rule={editingRuleState || { protocol: rule.protocol, portsString: rule.ports.join(", ") }}
                onSave={handleSaveRule}
                onCancel={() => {
                  setEditingRule(null);
                  setEditingRuleState(null);
                }}
                onChange={handleRuleChange}
              />
            ) : (
              <div
                key={`${rule.protocol}-${rule.ports.join(",")}`}
                className="flex items-center justify-between rounded-lg bg-gray-50 p-4 dark:bg-gray-700"
              >
                <div className="flex items-center gap-4">
                  <span className="text-sm font-medium text-gray-500 dark:text-gray-400">
                    Ports:
                  </span>
                  <span className="font-mono text-gray-900 dark:text-white">
                    {rule.ports.join(", ")}
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
