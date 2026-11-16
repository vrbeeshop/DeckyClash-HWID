import { t } from "i18next";

import { L } from "./i18n";

export enum SubscriptionError {
  HwidMaxDevicesReached = "HWID_MAX_DEVICES_REACHED",
  RequestFailed = "SUBSCRIPTION_REQUEST_FAILED",
}

export const localizeSubscriptionError = (error?: string | null): string => {
  switch (error) {
    case SubscriptionError.HwidMaxDevicesReached:
      return t(L.HWID_MAX_DEVICES_REACHED);
    case SubscriptionError.RequestFailed:
      return t(L.SUBSCRIPTION_REQUEST_FAILED);
    default:
      return error || "";
  }
};
