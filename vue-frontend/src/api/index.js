const BASE='/api'

async function request(url,options={}){
    const token =localStorage.getItem('token')
    const headers={
        'Content-Type':'application/json',
        ...(token?{Authorization:`Bearer ${token}`}:{}),
        ...options.headers
    }

    const res=await fetch(`${BASE}${url}`,{...options,headers})
    const data=await res.json()

    if (res.status===401){
        localStorage.removeItem('token')
        localStorage.removeItem('userName')
        window.location.href='/login'
    }

    return data
}

export function login(body){
    return request('/login',{method:"POST",body:JSON.stringify(body)})
}

export function register(body){
    return request('/register',{method:'POST',body:JSON.stringify(body)})
}

export function getEmployees(){
    return request('/employee',{method:"GET"})
}

export function updateEmployee(empId,body){
    return request(`/employee/${empId}`,{method:"PUT",body:JSON.stringify(body)})
}

