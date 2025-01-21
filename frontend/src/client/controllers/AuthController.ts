import { TLoginForm, TSignUpForm, TUser } from "../api/models/request";
import { TAuthResponse } from "../api/models/response";
import { AuthService } from "../services/auth";

export class AuthController {
  public static async login(credentials: TLoginForm): Promise<TAuthResponse> {
    try {
      const response = await AuthService.login(credentials);
      return response;
    } catch (error) {
      throw new Error("Login failed");
    }
  }

  public static async signup(formData: TSignUpForm): Promise<TAuthResponse> {
    try {
      const response = await AuthService.signup(formData);
      return response;
    } catch (error) {
      throw new Error("Signup failed");
    }
  }

  public static async logout(): Promise<void> {
    try {
      await AuthService.logout();
    } catch (error) {
      throw new Error("Logout failed");
    }
  }

  public static async refreshToken(): Promise<TAuthResponse> {
    try {
      const response = await AuthService.refreshToken();
      return response;
    } catch (error) {
      throw new Error("Token refresh failed");
    }
  }

  public static async getCurrentUser(): Promise<TUser> {
    try {
      const user = await AuthService.readUser();
      return user;
    } catch (error) {
      throw new Error("Failed to fetch user data");
    }
  }
}
