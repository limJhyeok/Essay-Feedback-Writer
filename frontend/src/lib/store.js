import { writable } from "svelte/store";

const persist_storage = (key, initValue) => {
  const storedValueStr = localStorage.getItem(key)
  const store = writable(storedValueStr != null ? JSON.parse(storedValueStr) : initValue)
  store.subscribe((val) => {
    localStorage.setItem(key, JSON.stringify(val))
  })
  return store
}

export const isLogin = persist_storage("isLogin", false)
export const userEmail = persist_storage("userEmail", "")
export const accessToken = persist_storage("accessToken", "")
export const isSignUpPage = persist_storage("isSignUpPage", false)
