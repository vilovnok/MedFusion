import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ChatService } from '../services/chat.service';
import { Router } from '@angular/router';
import { NgToastService } from 'ng-angular-popup';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent {
  loginForm!: FormGroup;
  
  constructor(
    private fb: FormBuilder, 
    private service: ChatService,
    private router: Router,
    private toaster: NgToastService
  ) {}

  ngOnInit(): void {
    this.valid_fun();
    this.service.rmFromLS('user_id');
  }

  valid_fun(): void {
    this.loginForm = this.fb.group({
      email: ['', Validators.required],
      password: ['', Validators.required]
    });
  }

  onLogin() {
    if (this.loginForm.valid) {
      this.service.handle_post_requests(this.loginForm.value,'auth/login').subscribe({
        next: (res) => {
          this.loginForm.reset();
          this.service.saveToLS('user_id', res.user_id);
          this.toaster.success({ detail: "SUCCESS", summary: res.message });
          this.router.navigate(['agent']);
        },
        error: (err) => {
          if (err.status === 422) {
            this.toaster.error({detail:"ERROR", summary: 'Проверьте передаваемые данные.' });
            return;
          }
          this.toaster.error({detail:"ERROR", summary: err.error.detail })
        }});
    } else {
      this.toaster.error({detail:"ERROR", summary:"Пожалуйста, зполните форму 😅️️️️️️❌️️️️️️️", duration: 5000});
    }
  }

  go_to_Reg(){
    this.router.navigate(['reg']);
  }
}
