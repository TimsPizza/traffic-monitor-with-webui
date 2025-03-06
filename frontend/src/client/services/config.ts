import { AxiosError } from "axios";
import { ConfigApi } from "../api/requests";
import type {
  ICaptureFilter,
  IProtocolPortMappingRule,
} from "../api/models/request";
import type {
  IFilterAllResponse,
  IProtocolPortMappingResponse,
  INetworkInterfacesResponse,
} from "../api/models/response";

class ConfigService {
  /**
   * 获取所有网络接口
   * Get all network interfaces
   */
  async getInterfaces(): Promise<INetworkInterfacesResponse> {
    try {
      const response = await ConfigApi.getInterfaces();
      return response.data;
    } catch (error) {
      console.error("Failed to get interfaces:", error);
      throw error as AxiosError;
    }
  }

  /**
   * 设置网络接口
   * Set network interface
   */
  async setInterface(interfaceName: string): Promise<boolean> {
    try {
      await ConfigApi.setInterface(interfaceName);
      return true;
    } catch (error) {
      console.error("Failed to set interface:", error);
      return false;
    }
  }

  /**
   * 获取所有端口映射规则
   * Get all port mapping rules
   */
  async getRules(): Promise<IProtocolPortMappingResponse> {
    try {
      const resp = await ConfigApi.getRules();
      return resp.data;
    } catch (e) {
      console.log("Failed to get rules:", e);
      throw e as AxiosError;
    }
  }

  /**
   * 添加或更新端口映射规则
   * Add or update port mapping rule
   */
  async addOrUpdateRule(
    rule: IProtocolPortMappingRule,
  ): Promise<IProtocolPortMappingResponse> {
    try {
      const resp = await ConfigApi.addOrUpdateRule(rule);
      return resp.data;
    } catch (e) {
      console.log("Failed to add or update rule:", e);
      throw e as AxiosError;
    }
  }

  /**
   * 删除端口映射规则
   * Delete port mapping rule
   */
  async deleteRule(
    rule: IProtocolPortMappingRule,
  ): Promise<IProtocolPortMappingResponse> {
    try {
      const response = await ConfigApi.deleteRule(rule);
      return response.data;
    } catch (e) {
      console.log("Failed to delete rule:", e);
      throw e as AxiosError;
    }
  }

  /**
   * 获取所有过滤器
   * Get all filters
   */
  async getFilters(): Promise<IFilterAllResponse> {
    return await ConfigApi.getFilters();
  }

  /**
   * 设置过滤器
   * Set filters
   */
  async setFilters(filters: ICaptureFilter[]): Promise<ICaptureFilter[]> {
    return await ConfigApi.setFilters(filters);
  }
}

export const configService = new ConfigService();
