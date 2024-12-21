import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { ChatService } from '../services/chat.service';
import { NgToastService } from 'ng-angular-popup';

@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.scss']
})
export class RegisterComponent implements OnInit {


  registerForm!: FormGroup;

  constructor(
    private fb: FormBuilder,
    private service: ChatService,
    private toaster: NgToastService,
    private router: Router
  ) { }


  ngOnInit(): void {
    this.valid_fun();
    this.service.rmFromLS('token');
    this.service.rmFromLS('user_id');
  }

  valid_fun(): void {
    this.registerForm = this.fb.group({
      username: ['', Validators.required],
      password: ['', Validators.required],
    });
  }


  onReg() {
    this.router.navigate(['agent']);
    if (this.registerForm.valid) {
      this.service.handle_post_requests(this.registerForm.value, 'auth/register').subscribe({
        next: (res) => {
          
          this.registerForm.reset();
          this.service.saveToLS('user_id', res.user_id);
          this.toaster.success({ detail: "SUCCESS", summary: res.message });
          this.router.navigate(['agent']);
        },
        error: (err) => {
          if (err.status === 422){
            this.toaster.error({
              detail: "❌ ERROR",
              summary: "Пожалуйста, проверьте вами введённые данные 🔍"
            });
          return;            
          }          
          this.toaster.error({ detail: "❌️️️️️️️ ERROR", summary: err.error.detail })
        }
      });
    } else {
      this.toaster.error({ detail: "❌️️️️️️️ ERROR", summary: "Пожалуйста, зполните форму 😅️️️️️️", duration: 5000 });
    }
  }
}
