import qs from "qs"
import { accessToken, userEmail, isLogin } from "./store"
import { get } from 'svelte/store'
import { push } from 'svelte-spa-router'

// Internal: shared response handler
function _handleResponse(response, operation, success_callback, failure_callback) {
    if (response.status === 204) {  // No content
        if (success_callback) {
            success_callback()
        }
        return
    }
    response.json()
        .then(json => {
            if (response.status >= 200 && response.status < 300) {  // 200 ~ 299
                if (success_callback) {
                    success_callback(json)
                }
            } else if (operation !== 'login' && response.status === 401) {  // token time out
                accessToken.set('')
                userEmail.set('')
                isLogin.set(false)
                push('/authorize')
            } else {
                if (failure_callback) {
                    failure_callback(json)
                } else {
                    alert(JSON.stringify(json))
                }
            }
        })
        .catch(error => {
            alert(JSON.stringify(error))
        })
}

// Internal: shared network error handler
function _handleNetworkError(failure_callback) {
    const errorMsg = { detail: "Network error. Please check your connection and try again." }
    if (failure_callback) {
        failure_callback(errorMsg)
    } else {
        alert(errorMsg.detail)
    }
}

const fastapi = (operation, url, params, success_callback, failure_callback) => {
    let method = operation
    let content_type = 'application/json'
    let body = JSON.stringify(params)

    if (operation === 'login') {
        method = 'post'
        content_type = 'application/x-www-form-urlencoded'
        body = qs.stringify(params)
    }

    let _url = import.meta.env.VITE_SERVER_URL + url
    if (method === 'get') {
        _url += "?" + new URLSearchParams(params)
    }

    let options = {
        method: method,
        headers: {
            "Content-Type": content_type
        }
    }

    const _access_token = get(accessToken)
    if (_access_token) {
        options.headers["Authorization"] = "Bearer " + _access_token
    }

    if (method !== 'get') {
        options['body'] = body
    }

    fetch(_url, options)
        .then(response => _handleResponse(response, operation, success_callback, failure_callback))
        .catch(() => _handleNetworkError(failure_callback))
}

export const fastapiUpload = (url, formData, success_callback, failure_callback) => {
    let _url = import.meta.env.VITE_SERVER_URL + url

    let options = {
        method: 'post',
        headers: {},
        body: formData,
    }

    const _access_token = get(accessToken)
    if (_access_token) {
        options.headers["Authorization"] = "Bearer " + _access_token
    }

    fetch(_url, options)
        .then(response => _handleResponse(response, 'upload', success_callback, failure_callback))
        .catch(() => _handleNetworkError(failure_callback))
}

export async function apiCall(operation, url, params) {
    return new Promise((resolve, reject) => {
        fastapi(operation, url, params, resolve, reject)
    })
}

export default fastapi
