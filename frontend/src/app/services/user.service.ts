import { HttpClient, HttpRequest, HttpResponse } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { concat, concatMap, Observable, Subject } from 'rxjs';
import { environment } from 'src/environments/environment';


@Injectable({
  providedIn: 'root'
})
export class UserService {

  private address = environment.API_BASE_URL;
  constructor(private http: HttpClient) { }


  handle_post_requests(userObject: any, endpoint: string) {
    return this.http.post<any>(`${this.address}/${endpoint}`, userObject)
  }

  handle_get_requests(userObject: any, endpoint: string) {
    return this.http.get<any>(`${this.address}/${endpoint}/${userObject}`)
  }

  healthcheck(endpoint: string) {
    return this.http.get<any>(`${this.address}/${endpoint}`)
  }

  getMessages(): Observable<any> {
    return this.http.get<any>(`${this.address}/messages`);
  }




}
