import { TLoginForm, TSignUpForm, TUser } from "../api/models/request";
import { TAuthResponse } from "../api/models/response";
import { AuthApi } from "../api/requests";

export class AuthService {
  public static login(formData: TLoginForm): Promise<TAuthResponse> {
    return AuthApi.login(formData);
  }

  public static signup(formData: TSignUpForm): Promise<TAuthResponse> {
    return AuthApi.signup(formData);
  }

  public static logout(): Promise<void> {
    return AuthApi.logout();
  }

  public static refreshToken(): Promise<TAuthResponse> {
    return AuthApi.refreshToken();
  }

  public static async readUser(): Promise<TUser> {
    // TODO: Implement user read logic
    throw new Error("Not implemented");
  }
}
